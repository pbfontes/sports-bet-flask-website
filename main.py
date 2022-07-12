from flask import Flask
#from DBconfig import collection

app = Flask(__name__)


@app.route("/")
def hello_world():
    # x = collection.find_one()
    # x1 = x["name"]
    # x2 = x["address"]
    # return f"<h1>{x1}, {x2}</h1>"
    return "teste"


if __name__ == '__main__':
    app.run()
