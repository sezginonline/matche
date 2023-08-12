from sanic import Blueprint
from sqlalchemy import select
from app.models.user import User
from app.services.auth import check_wss_hash
import json
import datetime

websocket = Blueprint("websocket", url_prefix="/wss")

MAX_INT32 = 2**31 - 1  # maximum value for an int32


@websocket.websocket('/')
async def main(request, ws):
    uid = request.args.get("uid")
    token = request.args.get("token")

    if not uid or not token or not str(uid).isdigit() or int(uid) > MAX_INT32 or int(uid) <= 0:
        return
    
    uid = int(uid)

    # Get user from DB
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.id == uid)
        result = await connection.execute(stmt)
        user = result.scalar()

    # User not found
    if not user:
        return
    
    # If user login attempt is high
    if user.login_attempt > 5:
        return

    # If wrong token
    if not check_wss_hash(user, token):
        user.login_attempt += 1
        await connection.commit()
        return

    # Register
    broadcast = request.app.ctx.broadcast
    if not await broadcast.register(ws, uid):
        return

    # Start
    try:
        async for message in ws:
            msg_json = json.loads(message)
            msg_json["uid"] = uid
            msg_with_uid = json.dumps(msg_json)

            # Insert to MongoDB
            if "type" in msg_json and msg_json["type"] == "broadcaster":
                current_time_utc = datetime.datetime.utcnow().isoformat()
                request.app.ctx.broadcasts.update_one(
                    {'user_id': uid},
                    {
                        '$set': {
                            'name': user.name,
                            'picture': user.picture,
                            'created': current_time_utc,
                            'is_active': True,
                        }
                    },
                    upsert=True
                )
            
            await broadcast.publish(msg_with_uid)
    finally:
        # Update is_active to False
        request.app.ctx.broadcasts.update_one(
            {'user_id': uid},
            {
                '$set': {
                    'is_active': False,
                }
            }
        )
        await broadcast.unregister(uid)
