from dotenv import find_dotenv, load_dotenv
from os import getenv
import pymongo
import json
from bson import json_util

place = find_dotenv()
load_dotenv(place)

USER_NAME = getenv("USER_NAME")
PASSWORD = getenv("PASSWORD")
CLIENT = getenv("CLIENT")

myclient = pymongo.MongoClient(
    f"mongodb+srv://{USER_NAME}:{PASSWORD}@{CLIENT}")
mydb = myclient["mydatabase"]
collection_customers = mydb["customers"]
collection_events = mydb["events"]


def parse_json(data):
    return json.loads(json_util.dumps(data))
