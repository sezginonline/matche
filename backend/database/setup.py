from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.matche

message_schema = {
    'senderId': {'type': 'integer', 'required': True},
    'receiverId': {'type': 'integer', 'required': True},
    'text': {'type': 'string', 'required': True}
}
message_collection = db['messages']
message_collection.create_index([('senderId', 1), ('receiverId', 1)])
message_collection.create_index([('receiverId', 1), ('senderId', 1)])

broadcast_collection = db['broadcasts']
broadcast_collection.create_index([('user_id', 1)], unique=True)
broadcast_collection.create_index([('is_active', 1)])

profile_collection = db['profiles']
profile_collection.create_index([('user_id', 1)], unique=True)
