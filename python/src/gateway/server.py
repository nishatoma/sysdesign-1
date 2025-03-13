import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

# Mongo DB
# Wrap our flask server which allows us to interface
# with MDB
mongo = PyMongo(server)

# Grid FS, enable us to use mongo db grid FS
# Mongo DB stores our files, both mp3 and video.
# If you see, binary json document size has max 16MB.

fs = gridfs.GridFS(mongo.db)

#Rabbit MQ config
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

# Routes =======================

# Login
@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err

# Upload route
@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) != 1:
            return "exactly 1 file required", 400
        
        first_file = next(request.files.items())
        
        err = util.upload(first_file, fs, channel, access)

        if err:
            return err
        return "success!", 200
    else:
        return "not authorized", 
        
@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)