from sanic import Blueprint, json
from sqlalchemy import select, func
from app.models.user import User
from datetime import datetime

import bcrypt

from app.services.auth import invalid, user_login, valid_email, valid_captcha, google_sign_in, decode_jwt
from app.languages.lang import _
from app.constants.user import UserStatus
from app.services.auth import rnd

auth = Blueprint("auth", url_prefix="/auth")


@auth.post("/login")
async def login(request):

    if not request.json:
        return invalid(request)

    email = request.json.get("email", "").strip()
    password = request.json.get("password", "").strip()
    captcha = request.json.get("g-recaptcha-response", "").strip()

    # Check email
    if not valid_email(email) or not password:
        return invalid(request)

    # Validate captcha
    if not await valid_captcha(captcha):
        return json({"message": _(request, "main.invalid_captcha")}, status=400)

    # Get user from DB
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.email == email)
        result = await connection.execute(stmt)
        user = result.scalar()
    if not user:
        return invalid(request)

    # Successful login
    if user.password and bcrypt.checkpw(password.encode(), user.password.encode()):
        response = await user_login(request, user)
        user.login_attempt = 0
        user.updated_at = datetime.utcnow()
        user.updated_ip = request.remote_addr
        await connection.commit()
        return response

    # Invalid credentials
    user.login_attempt += 1
    await connection.commit()
    return invalid(request)


@auth.post("/register")
async def register(request):

    if not request.json:
        return invalid(request)

    name = request.json.get("name", "").strip()
    email = request.json.get("email", "").strip()
    password = request.json.get("password", "").strip()
    captcha = request.json.get("g-recaptcha-response", "").strip()

    # Check email, password, name
    if not valid_email(email) or not password or not name:
        return invalid(request)

    # Validate captcha
    if not await valid_captcha(captcha):
        return json({"message": _(request, "main.invalid_captcha")}, status=400)

    # Define connection
    connection = request.ctx.connection
    async with connection.begin():

        # Check if email already exists
        stmt = select(User).where(User.email == email)
        result = await connection.execute(stmt)
        existing_user = result.scalar()
        if existing_user:
            return json({"message": _(request, "main.email_in_use")}, status=400)

        # Insert user
        user = User(name=name, email=email)
        user.password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()).decode()
        user.created_ip = request.remote_addr
        user.status = UserStatus.PASSIVE
        connection.add(user)
        await connection.commit()

    # If not added
    if not user.id:
        return invalid(request)
    
    # Make sure there is only 1 user with same email, to avoid race condition
    async with connection.begin():
        stmt = select(func.count(User.id)).where(User.email == email)
        result = await connection.execute(stmt)
        count = result.scalar()
        if count > 1:
            return json({"message": _(request, "main.email_in_use")}, status=400)
        else:
            user.status = UserStatus.ACTIVE
            await connection.commit()

    # Successful login
    response = await user_login(request, user)
    return response


@auth.post("/refresh")
async def refresh(request):

    refresh_token = request.cookies.get("REFRESH-TOKEN")
    auth_header = request.headers.get("Authorization")
    if auth_header:
        refresh_token = auth_header.replace("Bearer ", "")

    try:
        decoded = decode_jwt(refresh_token)
        user_id = decoded["sub"]
        refresh_token = decoded["iss"]
    except:
        return invalid(request)

    if not user_id or not refresh_token:
        return invalid(request)

    # Get user from DB
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.id == user_id)
        result = await connection.execute(stmt)
        user = result.scalar()
    if not user:
        return invalid(request)

    # Validate token
    if refresh_token == user.refresh_token:

        # Rotate refresh token
        user.refresh_token = rnd()
        await connection.commit()

        # Login
        return await user_login(request, user)

    return invalid(request)


@auth.post("/google")
async def google(request):
    credential = request.json.get("credential", "").strip()

    # Check credential
    if not credential:
        return invalid(request)

    idinfo = google_sign_in(credential)

    if not idinfo:
        return invalid(request)

    # Get user from DB
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.email == idinfo["email"])
        result = await connection.execute(stmt)
        user = result.scalar()

    # User found
    if user:

        # Email has to be verified to login
        if not idinfo["email_verified"]:
            return json({"message": _(request, "main.email_not_verified")}, status=400)

        # Successful login
        response = await user_login(request, user)
        user.login_attempt = 0
        user.email_verified = True
        user.updated_at = datetime.utcnow()
        user.updated_ip = request.remote_addr
        await connection.commit()
        return response

    # User not found, create user
    async with connection.begin():
        user = User(name=idinfo["name"], email=idinfo["email"])
        user.email_verified = idinfo["email_verified"]
        user.picture = idinfo["picture"].replace("=s96-c", "=s0-c")
        user.status = UserStatus.PASSIVE
        user.created_ip = request.remote_addr
        connection.add(user)
        await connection.commit()

    if not user.id:
        return invalid(request)

    # Make sure there is only 1 user with same email, to avoid race condition
    async with connection.begin():
        stmt = select(func.count(User.id)).where(User.email == idinfo["email"])
        result = await connection.execute(stmt)
        count = result.scalar()
        if count > 1:
            return json({"message": _(request, "main.email_in_use")}, status=400)
        else:
            user.status = UserStatus.ACTIVE
            await connection.commit()

    # Successful login
    response = await user_login(request, user)
    return response
