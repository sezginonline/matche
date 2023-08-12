from sanic import Sanic, json
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests

import jwt
import time
import datetime
import uuid
import re
import aiohttp
import bcrypt

from app.languages.lang import _
from app.constants.user import UserStatus


def auth(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            access_token = request.cookies.get("ACCESS-TOKEN")
            auth_header = request.headers.get("Authorization")
            if auth_header:
                access_token = auth_header.replace("Bearer ", "")

            try:
                request.ctx.user_id = decode_jwt(access_token)["sub"]
            except:
                return json({"message": "Unauthorized."}, status=401)

            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator(wrapped)


def decode_jwt(token):
    app = Sanic.get_app()

    try:
        return jwt.decode(token, app.config.JWT_SECRET, algorithms=["HS256"])
    except:
        if app.config.JWT_SECRET_OLD:
            return jwt.decode(token, app.config.JWT_SECRET_OLD, algorithms=["HS256"])


async def user_login(request, user):

    if (user.status < UserStatus.ACTIVE):
        return invalid(request)
    
    # In deletion status, user logged in, change status to active
    if (user.status == UserStatus.DELETION):
        request.ctx.connection.begin()
        user.status = UserStatus.ACTIVE
        await request.ctx.connection.commit()

    access_token = jwt.encode({"sub": user.id,
                               "exp": time.time() + 60 * 60},
                              request.app.config.JWT_SECRET, algorithm="HS256")

    refresh_token = jwt.encode({"sub": user.id, "iss": user.refresh_token,
                                "exp": time.time() + 60 * 60 * 24 * 30},
                               request.app.config.JWT_SECRET, algorithm="HS256")

    # Create response
    response = json({"access_token": access_token,
                    "refresh_token": refresh_token})

    # Create cookies
    response.add_cookie(
        "ACCESS-TOKEN",
        access_token,
        secure=True,
        httponly=True,
        samesite="Strict"
    )

    expires = None
    if request.json and request.json.get("remember"):
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)

    response.add_cookie(
        "REFRESH-TOKEN",
        refresh_token,
        secure=True,
        httponly=True,
        samesite="Strict",
        expires=expires
    )

    # Delete Google cookie, which interrupts other cookies
    response.delete_cookie("g_state")

    # Return the fuck
    return response


def invalid(request):
    return json({"message": _(request, "main.invalid_credentials")}, status=400)


def rnd():
    return uuid.uuid4().hex


def valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.fullmatch(regex, email)


async def valid_captcha(captcha):
    if not captcha:
        return False

    async with aiohttp.ClientSession() as http:
        async with http.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": Sanic.get_app().config.CAPTCHA_SECRET_KEY,
                "response": captcha,
            },
        ) as resp:
            result = await resp.json()
            if result["success"]:
                return True
            return False


def google_sign_in(token):
    # time.sleep(3)  # Prevent "Token used too early" error from Google
    try:
        return id_token.verify_oauth2_token(token, requests.Request(), Sanic.get_app().config.GOOGLE_CLIENT_ID)
    except ValueError as e:
        # print(e)
        return False


def get_wss_token(user):
    return str(user.id) + "|" + user.refresh_token[:10]


def create_wss_hash(user):
    return bcrypt.hashpw(get_wss_token(user).encode(), bcrypt.gensalt()).decode()


def check_wss_hash(user, token):
    return bcrypt.checkpw(get_wss_token(user).encode(), token.encode())
