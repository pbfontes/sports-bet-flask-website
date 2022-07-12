from dotenv import find_dotenv, load_dotenv
from os import getenv
import pymongo

place = find_dotenv()
load_dotenv(place)

USER_NAME = getenv("USER_NAME")
PASSWORD = getenv("PASSWORD")
CLIENT = getenv("CLIENT")

myclient = pymongo.MongoClient(
    f"mongodb+srv://{USER_NAME}:{PASSWORD}@{CLIENT}")
mydb = myclient["mydatabase"]
collection = mydb["customers"]
