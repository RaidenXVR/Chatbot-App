import openai
import json
import requests
import io
import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

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

    message = []
    message.extend(user["topics"][topic])
    message.append({"role": "user", "content": input})
    message.append(response)
    data = {"topics": {topic: message}}
    col.update_one({"_id": user_id}, {"$set": data})

    return message[-1]["content"]


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

    topic = generate_response(message)["content"]

    # Remove extra quotes and return the cleaned string
    if '"' in topic or "'" in topic:
        topic = topic.replace('"', "").replace("'", "")

    message = []
    message.append(
        {
            "role": "system",
            "content": "You are an elite Teacher. And I am your friend whom you must pass on your knowledge and expertise. In a series of sessions, you have to fulfil this duty and help me answer my questions. Be friendly and informal as I am your friend. Don't answer too long, use 2 paragraph or 6 sentences maximum.",
        }
    )
    message.append({"role": "user", "content": input})
    response = generate_response(message)
    if len(response["content"]) < 1:
        return
    else:
        message = []
        message.append({"role": "user", "content": input})
        message.append(response)
        col.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "topics": {topic: message},
                },
            },
        )
    return topic, response


def login(username: str, password: str):
    user = col.find_one({"username": username})

    if user == None:
        return False  # signup/username not found
    elif bcrypt.checkpw(password.encode("utf-8"), user["password"]):
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
    print(bcrypt.checkpw("80827".encode("utf-8"), hash_password))
    template = {
        "_id": count + 1,
        "username": username,
        "p": hash_password,
        "topics": {},
    }

    col.insert_one(template)
    return True  # account signup succesful


def generate_response(messages: list) -> str:
    openai.api_key = os.getenv("OPENAI_API")
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    return response["choices"][0]["message"]
