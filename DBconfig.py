from dotenv import find_dotenv, load_dotenv
from os import getenv
import pymongo
from json import loads
from bson import json_util

place = find_dotenv()
load_dotenv(place)

USER_NAME = getenv("USER_NAME")
PASSWORD = getenv("PASSWORD")
CLIENT = getenv("CLIENT")
APP_KEY = getenv("APP_SECRET_KEY")

myclient = pymongo.MongoClient(
    f"mongodb+srv://{USER_NAME}:{PASSWORD}@{CLIENT}")
mydb = myclient["test"]
collection_customers = mydb["customers"]
collection_events = mydb["eventdbs"]


def parse_json(data):
    return loads(json_util.dumps(data))


def extract_valid_id(str_obj):
    obj_id = str_obj.replace("'", '"')
    obj_id = loads(obj_id)
    obj_id = obj_id["$oid"]
    return obj_id
