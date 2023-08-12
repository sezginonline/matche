MAX_INT32 = 2**31 - 1  # maximum value for an int32

connected = {}


@websocket.websocket("/rtc12")
async def feed(request: Request, ws: Websocket):
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

    # User found
    if user and check_wss_hash(user, token):
        connected[uid] = ws
        try:
            async for message in ws:

                try:
                    msg_dict = json.loads(message)
                except:
                    continue

                if {"to", "msg"} <= msg_dict.keys() and str(msg_dict["to"]).isdigit():

                    to = int(msg_dict["to"])
                    msg = msg_dict["msg"]

                    if to in connected:
                        await connected[to].send(f"User {uid} says: {msg}")

                        # Persist the message in the database
                        message = Message(
                            from_user_id=uid,
                            to_user_id=to,
                            message=msg,
                        )
                        connection.add(message)
                        await connection.commit()

                    # Send a response to all connected clients except sender
                    # for conn in connected.values():
                    #    if conn != ws:
                    #        await conn.send(f"User {uid} says: {msg}")
        finally:
            connected.pop(uid)





clients = {}

@websocket.websocket('/rtc2')
async def rtc2(request, ws):
    clients.add(ws)
    try:
        while True:
            message = await ws.recv()
            data = json.loads(message)

            if 'sdp' in data:
                for client in clients:
                    if client is not ws:
                        await client.send(message)

            if 'ice' in data:
                for client in clients:
                    if client is not ws:
                        await client.send(message)
    finally:
        clients.remove(ws)


@websocket.websocket("/conn")
async def conn(request, ws):
    channel = request.app.ctx.channel
    client = await channel.register(ws)
    try:
        async for message in ws:
            await channel.publish(message)
    finally:
        await channel.unregister(client)


