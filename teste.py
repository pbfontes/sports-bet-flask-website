from DBconfig import collection_customers, collection_events, parse_json
from bson.objectid import ObjectId

query = {"_id": ObjectId("62d9714bf39764f20e3e8399")}
# newValues = {"$set": {"opcoes": event_data}}
newValues = {"$set": {"hora": "12:00"}}

x = collection_events.find(query)
for i in x:
    print(i)
# collection_events.update_one(query, newValues)
