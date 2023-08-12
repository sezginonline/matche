from sanic import Blueprint, Request, json
from sqlalchemy import select
from pydantic import BaseModel, constr, EmailStr

import bcrypt
import boto3
import imghdr
from io import BytesIO
from PIL import Image
from datetime import datetime

# import opennsfw2 as n2

from app.models.user import User
from app.services.auth import auth
from app.languages.lang import _
from app.services.auth import invalid
from app.constants.user import UserStatus

account = Blueprint("account", url_prefix="/account")


class UserInfo(BaseModel):
    name: constr(min_length=2) | None
    email: EmailStr | None
    password: str | None
    new_password: str | None
    delete: bool | None


@account.post("/info")
@auth
async def info(request):
    # Validate
    UserInfo(**request.json)

    name = request.json.get("name", "").strip()
    email = request.json.get("email", "").strip()
    password = request.json.get("password", "").strip()
    new_password = request.json.get("new_password", "").strip()
    delete = request.json.get("delete", "").strip()

    # Define connection
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.id == request.ctx.user_id)
        result = await connection.execute(stmt)
        user = result.scalar()

        if (name):
            user.name = name

        if (email != user.email):

            # Check if email already exists
            stmt = select(User).where(User.email == email)
            result = await connection.execute(stmt)
            existing_user = result.scalar()
            if not existing_user:
                user.email = email
                user.email_verified = False

        if (new_password and len(new_password) >= 8):
            if (not user.password or bcrypt.checkpw(password.encode(), user.password.encode())):
                user.password = bcrypt.hashpw(
                    new_password.encode(), bcrypt.gensalt()).decode()
            else:
                return invalid(request)

        if (delete):
            user.status = UserStatus.DELETION

        await connection.commit()

        return json(user.to_dict())


@account.route('/upload', methods=['POST'])
@auth
async def upload(request: Request):
    file = request.files.get("file")
    if not file or not imghdr.what(None, h=file.body):
        return json(False)

    S3_BUCKET = request.app.config.S3_BUCKET
    S3_REGION = request.app.config.S3_REGION
    AWS_ACCESS_KEY_ID = request.app.config.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = request.app.config.AWS_SECRET_ACCESS_KEY

    s3_client = boto3.client('s3', region_name=S3_REGION,
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Generate key for the uploaded file
    # key = file.name
    key = "user/" + str(request.ctx.user_id) + "/picture.jpg"

    # Open image from request body
    bytes_io = BytesIO(file.body)
    img = Image.open(bytes_io)

    # nsfw_probability = n2.predict_image(bytes_io)
    nsfw_probability = 0
    if (nsfw_probability > 0.10):
        return json({"message": "Oops!"}, status=400)

    # Crop the image to the desired aspect ratio
    width, height = img.size
    aspect_ratio = 1  # set desired aspect ratio here
    if width < height * aspect_ratio:
        # image is too tall, crop width
        new_width = height * aspect_ratio
        left = (width - new_width) // 2
        right = left + new_width
        img = img.crop((left, 0, right, height))
    elif height < width * aspect_ratio:
        # image is too wide, crop height
        new_height = width / aspect_ratio
        top = (height - new_height) // 2
        bottom = top + new_height
        img = img.crop((0, top, width, bottom))

    # Resize the image if it's larger than the desired size
    max_size = 800  # set desired max size here
    if img.size[0] > max_size or img.size[1] > max_size:
        img.thumbnail((max_size, max_size), resample=Image.LANCZOS)

    # Convert image to JPEG format and save it to memory buffer
    buffer = BytesIO()
    img.convert('RGB').save(buffer, 'JPEG', quality=85)

    # Upload file directly to S3
    response = s3_client.put_object(
        Bucket=S3_BUCKET, Key=key, Body=buffer.getvalue(), ACL='public-read')

    # Generate public URL for the uploaded file
    url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"

    # Save picture url in db
    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.id == request.ctx.user_id)
        result = await connection.execute(stmt)
        user = result.scalar()
        user.picture = url
        await connection.commit()

    return json({"url": url})


@account.route('/profile', methods=['POST'])
@auth
async def profile(request: Request):
    if not request.json:
        return invalid(request)

    gender = request.json.get("gender", "")
    looking = request.json.get("looking", [])
    age = int(request.json.get("age")) if request.json.get(
        "age").isdigit() else 0
    birthyear = 0
    if (age > 0):
        birthyear = datetime.now().year - int(age)
    height = int(request.json.get("height")) if request.json.get(
        "height").isdigit() else 0
    weight = int(request.json.get("weight")) if request.json.get(
        "weight").isdigit() else 0
    education = request.json.get("education", "")
    goal = request.json.get("goal", "")
    religion = request.json.get("religion", "").strip()
    relationship = request.json.get("relationship", "")
    bio = request.json.get("bio", "").strip()
    partner = request.json.get("partner", "").strip()
    city = request.json.get("city", "")
    region = request.json.get("region", "")
    country = request.json.get("country", "")
    location = request.json.get("location", "")
    point = None
    if location:
        location_array = location.split(",")
        latitude = float(location_array[0])
        longitude = float(location_array[1])
        point = {'type': 'Point', 'coordinates': [latitude, longitude]}

    connection = request.ctx.connection
    async with connection.begin():
        stmt = select(User).where(User.id == request.ctx.user_id)
        result = await connection.execute(stmt)
        user = result.scalar()

    request.app.ctx.profiles.update_one(
        {'user_id': request.ctx.user_id},
        {
            '$set': {
                'name': user.name,
                'picture': user.picture,
                'gender': gender,
                'age': age,
                'birthyear': birthyear,
                'looking': looking,
                'height': height,
                'weight': weight,
                'education': education,
                'goal': goal,
                'religion': religion,
                'relationship': relationship,
                'bio': bio,
                'partner': partner,
                'city': city,
                'region': region,
                'country': country,
                'location': point,
            }
        },
        upsert=True
    )

    return json({})


@account.route('/profile', methods=['GET'])
@auth
async def get_profile(request: Request):
    document = await request.app.ctx.profiles.find_one({'user_id': request.ctx.user_id})
    if document:
        # Remove the _id field from the document
        del document["_id"]
        return json(document)
    else:
        return json({"message": "Profile not found"}, status=404)
