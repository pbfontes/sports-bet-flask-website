from DBconfig import collection_events, parse_json
from flask import jsonify


def getEvents(filter):
    events = list()
    for element in collection_events.find():
        events.append(dict(element))
    return parse_json({"events": events})
