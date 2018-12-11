from datetime import datetime, timedelta
import json

import jwt
from pony.orm import db_session, commit
from werkzeug.security import check_password_hash

from app.db import User
from app.user_controller import UserController

class Auth():

    def encode_token(self, data, key="teste", algorithm="HS256", expire_time=timedelta(days=1)):
        data["exp"] = datetime.now() + expire_time
        token = jwt.encode(data, key, algorithm=algorithm)
        return token.decode("utf-8")

    def verify_token(self, token, key="teste", algorithm="HS256"):
        try:
            result = jwt.decode(token, key, algorithm=algorithm)
        except Exception as ex:
            result = None
        return result

    def expire_token(self, token, key="teste", algorithm="HS256"):
        result = jwt.decode(token, key, algorithm=algorithm)
        result["exp"] = datetime.utcnow() - timedelta(days=365)
        data = jwt.encode(result, key=key, algorithm=algorithm)
        return data.decode("utf-8")

    @db_session
    def autenticate(self, email, password):
        user = User.get(email=email)
        user_controller = UserController()
        if user and check_password_hash(user.password, password):
            user_data = user_controller.get_user(id=user.user_id, export_json=False)
            token = self.encode_token(data={"email": email, "role": user_data["role"]})
            user_data["token"] = token
            return json.dumps(user_data)
        return None

    def logout(self, token):
        return json.dumps({"token": self.expire_token(token)})

    @db_session
    def alter_password(self, user_id, password, new_password):
        user = User.get(id=user_id)
        passwd_encode  = self.encode_password(password)
        if user.password == passwd_encode:
            new_password_encode = self.encode_password(new_password)
            user.password = new_password_encode
            commit()
