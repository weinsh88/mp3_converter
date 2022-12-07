import json
import os

import gridfs
import pika
from auth_svc import access
from flask import Flask, request
from flask_pymongo import PyMongo
from storage import util

from auth import validate

server = Flask(__name__)

mongo_video = "mongodb://host.minikube.internal:20717/videos"

server.config["MONGO_URI"] = mongo_video

mongo_video = PyMongo(server)

fs = gridfs.GridFS(mongo_video.db)

credentials = pika.PlainCredentials('guest', 'guest')
conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))  # type: ignore
channel = conn.channel()


@server.route("/login", methods=["POST"])  # type: ignore
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload(): 
    access, err = validate.token(request)

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1: 
            return "exactly 1 file required", 400
        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access)

            if err:
                return err
        return "success!", 200

    else: 
        return "not authorized", 401



@server.route("/download", methods=["GET"])  # type: ignore
def download():
    pass




if __name__ == '__main__':
    server.run(host="0.0.0.0", port=8080)
