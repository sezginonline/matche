from sanic import Blueprint, json
from sqlalchemy import select

from app.models.user import User
from app.services.auth import auth
from app.languages.lang import _
from app.services.auth import create_wss_hash

users = Blueprint("users", url_prefix="/users")


@users.get("/me")
@auth
async def me(request):
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.id == request.ctx.user_id)
        result = await connection.execute(stmt)
        user = result.scalar()
    if not user:
        return json({"message": _(request, "main.user_not_found")}, status=400)
    user_dict = user.to_dict()
    user_dict["wss_token"] = create_wss_hash(user)
    return json(user_dict)


@users.get("/discover")
@auth
async def discover(request):
    page = int(request.args.get("page", 1))
    if (page > 10 or page < 1):
        return json([])
    limit = 10
    offset = page * limit - limit
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).filter(
            User.picture.isnot(None)).offset(offset).limit(limit)
        result = await connection.execute(stmt)
        users = result.all()
    return json([user[0].to_public() for user in users])


@users.post("/logout")
async def logout(request):
    response = json({"message": _(request, "main.logged_out")})
    response.delete_cookie("ACCESS-TOKEN")
    response.delete_cookie("REFRESH-TOKEN")
    return response
