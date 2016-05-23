from flask import Flask, render_template, request, json, redirect, session
from pymongo import MongoClient
import operator, requests
import os, re

app = Flask(__name__)
app.secret_key = 'Raijin:AQWER-WDSEE-DDEWE-WECEG'
client = MongoClient()
db = client['Raijin']

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html',name = 'Welcome ' + session.get('user'))
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            users = db.Users
            userEntry = {
                "userName": _name,
                "email": _email,
                "password": _password
                        }

            if users.find_one({"email": _email}) is None and users.find_one({"userName": _name}) is None:
                userid = users.insert_one(userEntry).inserted_id
                if userid:
                    return render_template('errorSignup.html',error = 'User created successfully. Please login')
                else:
                    return render_template('errorSignup.html',error = 'Oops something went wrong. Please try again')
            else:
                return render_template('errorSignup.html',error = 'User already exits. Please try again or log in to continue')
        else:
            return render_template('errorSignup.html',error = 'Please fill in all the required fields')

    except Exception as e:
        return render_template('errorSignup.html',error = str(e))


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        users = db.Users
        if _username and _password:
              if users.find_one({"email": _username} and {"password" : _password}) is not None:
                       session['user'] = users.find_one()['userName']
                       return redirect('/userHome')
              else:
                      return render_template('errorSignin.html',error = 'Wrong Email address or Password. Please try again')

    except Exception as e:
        return render_template('errorSignin.html',error = str(e))


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/getMovies')
def getMovies():
    movies = db.Movies
    movie_dic = []
    for movie in movies.find():
        movieJson = {
            'movieName': movie['movieName'],
            'movieCategory': movie['movieCategory'],
        }
        movie_dic.append(movieJson)
    movie_dic = sorted(movie_dic, key=lambda k : k['movieName'])
    return json.dumps(movie_dic)


@app.route('/userRatings',methods=['POST'])
def userRatings():
    try:
        ratings = {}
        movie_dic = {}
        movies = db.Movies
        userRatings = db.userRatings

        for movie in movies.find():
            movie_dic[movie['movieID']] = movie['movieName']
        movie_dic = sorted(movie_dic.items(), key=operator.itemgetter(1))
        for i in range(1,3884):
            if int(request.form["ratings["+str(i)+"]"]) != 0:
                ratings[(movie_dic[i-1][0])] = int(request.form["ratings["+str(i)+"]"])*2

        ratingJson = {
            'userName' : session.get('user'),
            'ratings' : ratings
        }

        if userRatings.find_one({"userName":  session.get('user')}):
             userRatings.remove({"userName":  session.get('user')})

        ratingid = userRatings.insert_one(ratingJson).inserted_id
        if ratingid is None:
           return render_template('error.html',error = 'Oopes : Unexpected Error')

        ratingFlie = open('user_ratings.file','w')
        for key,value in ratings.items():
            ratingFlie.write(str(key)+","+str(value)+"\n")
        ratingFlie.close()
        userid = str(0)

        cmd = "curl --data-binary @user_ratings.file http://127.0.0.1:5432/"+userid+"/ratings"

        for i in range(1,10):
            return_stat = os.system(cmd)
            if return_stat == 0:
                break

        if return_stat == 0:
            results = requests.get("http://127.0.0.1:5432/0/ratings/top/10")
            if results:
                recommendations = results.content
                recom_map = getRecommendations(recommendations,movies)
                userRecommendation = db.userRecommendations

                recomJson = {
                         'userName' : session.get('user'),
                          'recommendations' : recom_map
                        }

                if userRecommendation.find_one({"userName": session.get('user')}):
                    userRecommendation.remove({"userName":  session.get('user')})

                recomid = userRecommendation.insert_one(recomJson).inserted_id
                if recomid is None:
                    return render_template('error.html',error = 'Oopes : Unexpected Error')
                return redirect('/userRecommendations')
        else:
            return render_template('error.html',error = 'Oops : Unexpected Error')

    except Exception as e:
        return render_template('error.html',error = 'Oopes : Unexpected Error')

@app.route('/userRecommendations')
def userRecommendations():
    if session.get('user'):
        return render_template('userRecommendations.html',name = 'Welcome ' + session.get('user'))
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/fetchRecommendations')
def fetchRecommendations():
    recom = db.userRecommendations
    movies = db.Movies
    user = session.get('user')
    results = recom.find_one({"userName": user})['recommendations'].keys()
    resultList = []
    for id in results:
        rec = recom.find_one({"userName": user})['recommendations'][id].split(':')
        numRatings = rec[0]
        rating = rec[1]
        ratingJson = {
            'movieName': movies.find_one({'movieID':id})['movieName'],
            'movieCategory' : movies.find_one({'movieID':id})['movieCategory'],
            'movieRating': rating,
            'numRatings': numRatings
        }
        resultList.append(ratingJson)
    return json.dumps(resultList)



def getRecommendations(recommendations,movies):
    recommendations = recommendations[1:-1]
    list_recom =  re.findall(r"[^[]*\[([^]]*)\]", recommendations)
    list_cln = []
    for each in list_recom:
        tmp1 = re.findall(r"[^[]*\"([^]]*)\"", each)[0]
        tmp2 = each.split(",")
        movieID = movies.find_one({"movieName": tmp1})['movieID']
        tup = (movieID,tmp2[-1],tmp2[-2])
        list_cln.append(tup)
    recomMap = {}
    for each in list_cln:
        recomMap[each[0]] = str(each[1])+":"+str(each[2])
    return recomMap


if __name__ == "__main__":
    app.debug = True
    app.run(port=5002)
