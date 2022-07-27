from DBconfig import collection_events, parse_json, collection_customers, extract_valid_id
from flask import jsonify
from bson.objectid import ObjectId


def getEvents(filters, user_id=None):
    if filters["usage"] == "home":
        events = list()
        for element in collection_events.find():
            events.append(dict(element))
        return parse_json({"events": events})
    elif filters["usage"] == "profile" and user_id is not None:

        # encontrando eventos que o usuário apostou
        query_user = {"_id": ObjectId(extract_valid_id(user_id))}
        user = collection_customers.find_one(query_user)
        eventos = user["eventos-aportados"]

        # crazando com os eventos ativos
        query_events = {"status": "ativo", "_id": {"$in": eventos}}
        events = list()
        for element in collection_events.find(query_events):
            events.append(dict(element))
        return parse_json({"events": events})
    return None
