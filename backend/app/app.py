# Imports
from sanic import Sanic, json
from sanic.blueprints import Blueprint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextvars import ContextVar
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError

import aioredis
import logging
import os

from app.services.broadcast import Broadcast

from app.controllers.v1.auth import auth
from app.controllers.v1.account import account
from app.controllers.v1.users import users
from app.controllers.websocket import websocket
from app.controllers.index import index
from app.languages.lang import _

# Set paths
APP_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
ROOT_PATH = APP_PATH + '../'

# Define app
app = Sanic("Match-E")
app.update_config(ROOT_PATH + ".env")
app.config.TEMPLATING_PATH_TO_TEMPLATES = APP_PATH + "views"
app.config.CORS_ALLOW_HEADERS = "Content-Type,X-Requested-With,Authorization"

# Logging
if app.config.APP_ENV != "local":
    logging.config.dictConfig({
        'version': 1,
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': ROOT_PATH + 'logs/error.log',
                'encoding': 'utf-8',
                'level': 'ERROR'
            }
        },
        'loggers': {
            'sanic.root': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True
            },
            'sanic.error': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True
            }
        }
    })

# DB connection
bind = create_async_engine("postgresql+asyncpg://" + app.config.DB_STRING)
_sessionmaker = sessionmaker(bind, expire_on_commit=False, class_=AsyncSession)
_ctx = ContextVar("session")
app.ctx.mongo = AsyncIOMotorClient('mongodb://localhost:27017').matche
app.ctx.messages = app.ctx.mongo['messages']
app.ctx.profiles = app.ctx.mongo['profiles']
app.ctx.broadcasts = app.ctx.mongo['broadcasts']


@app.listener("before_server_start")
async def before_server_start(app):
    app.ctx.redis = aioredis.from_url(
        "redis://localhost", encoding="utf-8", decode_responses=True)
    await Broadcast.connect()


if app.config.APP_ENV != "local":
    @app.exception(Exception)
    async def catch_anything(request, exception):
        return json({"message": "An error occurred."}, status=404)


@app.middleware("request")
async def middleware_request(request):

    # CSRF
    if not request.method in ["GET", "OPTIONS"] and (
            # In file uploads Content-Type is not application/json, instead multipart/form-data; boundary=..
            # request.headers.get("Content-Type") != "application/json" or
            request.headers.get("X-Requested-With") != "XMLHttpRequest"):
        return json({"message": "CSRF protection."}, status=400)

    # For DB
    request.ctx.connection = _sessionmaker()
    request.ctx.connection_token = _ctx.set(request.ctx.connection)

    # Set language
    request.ctx.language = request.headers.get("Content-Language")


@app.middleware("response")
async def middleware_response(request, response):

    # CORS
    if request.headers.get("origin") == app.config.CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = app.config.CORS_ORIGINS
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"

    # For DB
    if hasattr(request.ctx, "connection_token"):
        _ctx.reset(request.ctx.connection_token)
        await request.ctx.connection.close()


@app.exception(ValidationError)
async def validation_error_handler(request, exception):
    errors = {}
    for error in exception.errors():
        field = '.'.join(error['loc'])
        error_message = error['msg']
        trans_msg = _(request, f"err.{error_message}")
        errors[field] = _(request, f"fields.{field}") + " " + trans_msg

    return json({"message": ", ".join(list(errors.values())), "errors": errors}, status=400)


# Router
app.blueprint(index)
app.blueprint(websocket)

v1 = Blueprint.group(auth, users, account,
                     version=1, version_prefix="/api/v")
app.blueprint(v1)
