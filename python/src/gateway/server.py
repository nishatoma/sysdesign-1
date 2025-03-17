import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)

mongo_video = PyMongo(server, uri="mongodb://kubernetes.docker.internal:27017/videos")
mongo_mp3 = PyMongo(server, uri="mongodb://kubernetes.docker.internal:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

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
        
        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401
        
@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)