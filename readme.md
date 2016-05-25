# RAIJIN - Movie Recommendation Engine (developed using Python Spark Library)

<h3>Introduction</h3>
Raijin is a movie recommendation engine which recommends movies to a user. The model has been trained on movie lens dataset using collaborating filtering (alternating least squares method). User rates a few movies on a scale of 5 (highest being 5 and loweset being 1) and the Raijin displays top 10 recommendations to the user. The ratings for other than top 10 movies can also be obtainied (not displayed though).

<h3>Technologies Used</h3>
1. API - Python, PySpark, Flask
2. Interface - Python, Flask, JS, JQuery, HTML
3. Database - MongoDB

<h3>Dataset - Movie Lens</h3>
Two sample datasets are there in Datasets folder
1. [MovieLens](http://grouplens.org/datasets/movielens/)
2. Traininig Data -  Due to the limitation of my machine, I trained the model on ml-1m dataset which has about 1 million ratings for 3952 movies. You can download larger datasets to train the model.
	 
<h3>Setup</h3>
1. Download and install the following : 
	i. [PySpark](https://spark.apache.org/docs/0.9.0/python-programming-guide.html)
	ii. Python 2.7.x with packages for [Flask](http://flask.pocoo.org/), MongoDB Client
	iii. [MongoDB](https://www.mongodb.com/download-center?jmp=nav#community)
2. Download the repository on your local machine
3. Download the dataset from [MovieLens](http://grouplens.org/datasets/movielens/) and put it in the Datasets folder. Please check for the format and delimiters used in the dataset for movies and ratings flies and make the necessary changes in the recomengine.py.
4. Set the necesssary paths for the dataset files in the properties.py
5. Create a new MongoDB database and set its path to the RaijinDB folder. Run the MongoDB servier and create the following collections in the database:	
	i. Movies - contains the records for all the movi
	ii. Users - contains the records for registered users
	iii. userRatings - contains the records for the ratings submitted by the user
	iv. userRecommendations - contains the recommendations generated by Raijin for the user

<h3>Run</h3>
1. Run app.py (inside RaijinEngine folder). This will run PySpark, train the model and deploy the Raijin API on local server.
2. Run app.py (inside RaijinInterface folder). This will deploy the frontend interface on local server. You can change the listening port (default is set to 5002)
3. Open the browser and type in http://IP Address:Port
4. Sign up to create an account on Raijin.
5. Sign in to your account.
6. User home page will show your recommendations. If this is a first login, rate a few movies and hit submit button to generate recommendations.
PS - Interface is a little shabby and not too bad for development and learning purpose. Enjoy :)