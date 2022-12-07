import datetime
import json
import os
from typing import Any

import jwt
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)


# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))


class DTEncoder(json.JSONEncoder): 
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime.datetime): 
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


@server.route("/login", methods=["POST"])  # type: ignore
def login(): 
    auth = request.authorization
    if not auth: 
        return "missing credentials", 401
    
    # check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    print(res)

    if res > 0: 
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else: 
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
        
    else: 
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate(): 
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt: 
        return "missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]

    try: 
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
    except Exception: 
        return "not authorized", 403
    
    return decoded, 200

# Gateway will send request to auth service which will generate a private
# key and shared via json web token. Future requests will include the auth
# token in the payload which is validated by auth service 


def createJWT(username, secret, authz): 
    
    payload = {
            "username": username, 
            "exp": json.dumps(datetime.datetime.now(tz=datetime.timezone.utc) 
            + datetime.timedelta(days=1), cls=DTEncoder),
            "iat": json.dumps(datetime.datetime.utcnow(), cls=DTEncoder), 
            "admin": authz,
        }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=5000)