import openai
import json
import requests
import io
import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv, set_key
import bcrypt
from openai import OpenAI, AsyncOpenAI
import base64
from PIL import Image
import asyncio

load_dotenv()
mongo_key = os.getenv("MONGO_DB")

client = MongoClient(mongo_key)
db = client["Chatbot"]
col = db["users"]


# for normal chat
def get_response(input: str, user_id: int, topic: str) -> str:
    user = col.find_one({"_id": user_id})
    message = [
        {
            "role": "system",
            "content": "You are an elite Teacher. And I am your friend whom you must pass on your knowledge and expertise. In a series of sessions, you have to fulfil this duty and help me answer my questions. Be friendly and informal as I am your friend.",
        },
    ]

    message.extend(user["topics"][topic])
    message.append({"role": "user", "content": input})

    response = generate_response(message)
    response = response.content

    message = []
    message.append(user["topics"][topic])
    message.append({"role": "user", "content": input})
    message.append({"role": "user", "content": response})

    topics: list = user["topics"]
    for tpc in topics:
        if topic in tpc.keys():
            tpc[topic] = message
    data = {"topics": topics}
    col.update_one({"_id": user_id}, {"$set": data})

    return message[-1]["content"], "chat"


# for first new topic chat
def get_first_response(input: str, user_id):
    user = col.find_one({"_id": user_id})
    message = []
    message.append(
        {
            "role": "system",
            "content": "Make a topic title from the user input. Send only the titles without any confirmations and don't use quotation marks or apostrophes.",
        }
    )
    message.append({"role": "user", "content": input})

    topic = generate_response(message)
    topic = topic.content

    # Remove extra quotes and return the cleaned string
    if '"' in topic or "'" in topic:
        topic = topic.replace('"', "").replace("'", "")

    message = []
    message.append(
        {
            "role": "system",
            "content": "You are an elite Teacher. And I am your friend whom you must pass on your knowledge and expertise. In a series of sessions, you have to fulfil this duty and help me answer my questions. Be friendly and informal as I am your friend. Answer shortly, just answer or do as they say.",
        }
    )
    message.append({"role": "user", "content": input})
    response = generate_response(message)
    if len(response.content) < 1:
        return
    else:
        message = []
        message.append({"role": "user", "content": input})
        message.append({"role": "assistant", "content": response.content})
        topics: list = user["topics"]
        topics.append({topic: message})
        col.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "topics": topics,
                },
            },
        )
    return response.content, topic


def login(username: str, password: str):
    user = col.find_one({"username": username})

    if user == None:
        return False  # signup/username not found
    elif bcrypt.checkpw(password.encode("utf-8"), user["p"]):
        return True
    else:
        return False  # wrong password


def sign_up(username: str, password: str):
    count = col.estimated_document_count()
    users = col.find_one({"username": username})
    if users != None:
        return False  # username already in use

    hash_password = bcrypt.hashpw(
        password=password.encode("utf-8"), salt=bcrypt.gensalt()
    )
    user_id = count + 1
    set_key(".env", "USER_ID", user_id)
    print(bcrypt.checkpw("80827".encode("utf-8"), hash_password))
    template = {
        "_id": user_id,
        "username": username,
        "p": hash_password,
        "topics": [],
        "button": [],
    }

    col.insert_one(template)
    return True  # account signup succesful


def generate_response(messages: list = None, prompt: str = None) -> str:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API"))
    if not prompt == None:
        messages = [{"role": "user", "content": prompt}]
    response = openai_client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages
    )
    return response.choices[0].message


def generate_image(prompt: str):
    openai.api_key = os.getenv("OPENAI_API")
    response = openai.images.generate(
        prompt=prompt,
        model="dall-e-3",
        quality="standard",
        response_format="b64_json",
        size="1024x1024",
        n=1,
    )

    tm = time.strftime("%d%m%Y-%H.%M%S")
    image64 = response.data[0].b64_json

    image_data = base64.b64decode(image64)
    image = Image.open(image_data)
    if not os.path.exists("./img"):
        os.mkdir("./img")
    image.save(f"./img/{tm}.png")


def test_input(input: str, type: str):
    time.sleep(3)

    return input, type


# async def gen_response(messages: list = None, prompt: str = None):
#     response = await generate_response(messages=messages, prompt=prompt)
#     return response
