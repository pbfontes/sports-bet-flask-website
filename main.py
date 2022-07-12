from flask import Flask, render_template
from DBconfig import collection

app = Flask(__name__)


@app.route("/")
def home():
    # x = collection.find_one()
    # x1 = x["name"]
    # x2 = x["address"]
    # f"<h1>{x1}, {x2}</h1>"
    return render_template("home.html")


if __name__ == '__main__':
    app.run()
