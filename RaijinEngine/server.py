import time, sys, cherrypy, os
from paste.translogger import TransLogger
from app import create_app

sys.path.append("C:/spark-1.5.2-bin-hadoop2.6/spark-1.5.2-bin-hadoop2.6/python/")

try:
    from pyspark import SparkContext, SparkConf
except ImportError as e:
    print ("Error in importing modules", e)
    sys.exit(1)


def init_spark_context():
    # load spark context
    conf = (SparkConf()
         .setMaster("local[4]")
         .setAppName("Raijin")
         .set("spark.executor.memory", "2g")
         .set("spark.driver.memory", "2g"))
    # IMPORTANT: pass aditional Python modules to each worker
    sc = SparkContext(conf=conf, pyFiles=["recomengine.py", "app.py"])
    return sc


def run_server(app):

    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload.on': True,
        'log.screen': True,
        'server.socket_port': 5432,
        'server.socket_host': '127.0.0.1'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == "__main__":
    # Init spark context and load libraries
    sc = init_spark_context()
    app = create_app(sc)

    # start web server
    run_server(app)