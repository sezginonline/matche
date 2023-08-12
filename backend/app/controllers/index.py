from sanic import Request, redirect
from sanic_ext import render
from sanic.blueprints import Blueprint
from app.languages.lang import lang
from faker import Faker
from app.models.user import User
from app.constants.user import UserStatus
import random

index = Blueprint("index", url_prefix="/")


@index.get("/", name="index")
@index.get("/<lng:[a-z]{2}>", name="index_lng")
async def index_lng(request: Request, lng: str = "en"):
    if (request.cookies.get("ACCESS-TOKEN") or request.cookies.get("REFRESH-TOKEN")):
        return redirect("/spa")
    if not lng in lang:
        return redirect("/")
    online = await request.app.ctx.redis.get("online")
    online_count = int(online or 0) + random.randint(340, 360) * 0
    return await render("index.html", context={
        "t": lang[lng],
        "captcha_site_key": request.app.config.CAPTCHA_SITE_KEY,
        "google_client_id": request.app.config.GOOGLE_CLIENT_ID,
        "online": online_count,
    })


@index.get("/<lng:[a-z]{2}>/<policy:(privacy|cookie|terms)>")
async def privacy(request: Request, lng: str, policy: str):
    if lng in lang:
        return await render("policy.html", context={"t": lang[lng], "policy": policy})
    return redirect("/")


@index.get("/faker")
async def faker(request: Request):

    # return redirect("/")

    connection = request.ctx.connection
    async with connection.begin():

        fake = Faker()
        fake.name()
        fake.email()

        user = User(name="Sezgin Serin", email="sezginonline@gmail.com")
        user.password = "$2b$12$0IjMZsb53JxjTiWb3qhrhu2EQc6aLY9kw3FaD9q/4E8/7uc1pN8Xm"
        user.email_verified = True
        user.picture = "https://match-e.s3.eu-central-1.amazonaws.com/user/21/picture.jpg"
        user.status = UserStatus.ACTIVE
        user.created_ip = request.remote_addr
        connection.add(user)
        
        for i in range(199):
            user = User(name=fake.name(), email=fake.email())
            user.password = "$2b$12$0IjMZsb53JxjTiWb3qhrhu2EQc6aLY9kw3FaD9q/4E8/7uc1pN8Xm"
            user.email_verified = True
            user.picture = fake.image_url(300, 300)
            user.status = UserStatus.ACTIVE
            user.created_ip = request.remote_addr
            connection.add(user)
        
        await connection.commit()

    return redirect("/")
