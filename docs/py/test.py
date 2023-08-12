
@app.get("/test")
async def test(request):
    document = await do_find(request)
    # return json(json_util.dumps(document))
    return json({"test": "ss"})


async def do_insert(request):
    request.app.ctx.messages.insert_one({
        'senderId': 2,
        'receiverId': 10,
        'text': "denemememde"
    })


async def do_select(request):
    document = await request.app.ctx.messages.find_one({'receiverId': 10})
    return document


async def do_find(request):

    user1 = 2
    user2 = 10

    query = {
        "$or": [
            {"senderId": user1, "receiverId": user2},
            {"senderId": user2, "receiverId": user1}
        ]
    }

    cursor = request.app.ctx.messages.find(query).limit(2)
    async for document in cursor:
        print(document["text"])


async def do_delete_many(request):
    await request.app.ctx.messages.delete_many({})
