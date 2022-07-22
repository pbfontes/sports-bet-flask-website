from flask import Flask, redirect, render_template, request
from DBconfig import collection_customers, collection_events, parse_json
from bson.objectid import ObjectId
from events_viewer import getEvents

app = Flask(__name__)


@app.route("/")
def home():
    # x = collection.find_one()
    # x1 = x["name"]
    # x2 = x["address"]
    # f"<h1>{x1}, {x2}</h1>"
    return render_template("home.html")


@app.route("/criar_evento")
def criar_evento():
    return render_template("creator.html")


@app.route("/checkNewEvent1", methods=["GET", "POST"])
def checkNewEvent1():
    if request.method == "POST":
        event_data = dict()
        titulo = request.form.get("inputTitulo")
        descricao = request.form.get("inputDescricao")
        dia = request.form.get("inputData")
        hora = request.form.get("inputHora")
        categoria = request.form.get("inputCategoria")

        event_data["titulo"] = titulo
        event_data["descricao"] = descricao
        event_data["dia"] = dia
        event_data["hora"] = hora
        event_data["categoria"] = categoria

        result = collection_events.insert_one(parse_json(event_data))

        print(result.inserted_id)

        return redirect(f"/selecionar_opcoes/{result.inserted_id}")
    return redirect("/criar_evento")


@app.route("/selecionar_opcoes/<event_id>")
def criar_evento2(event_id):
    return render_template("creator2.html", event_id=event_id)


@app.route("/checkNewEvent2/<event_id>", methods=["GET", "POST"])
def checkNewEvent2(event_id):
    if request.method == "POST":
        event_data = request.form.to_dict(flat=False)
        for option in event_data.keys():
            event_data[option] = event_data[option][0]

        print(event_data)

        query = {"_id": ObjectId(event_id)}
        newValues = {"$set": {"opcoes": event_data}}

        collection_events.update_one(query, newValues)

        return redirect("/")
    return redirect("/criar_evento")


@app.route("/cadastro")
def signup():
    return render_template("signup.html")


@app.route("/checkUserSignUp", methods=["GET", "POST"])
def checkUserSignUp():
    if request.method == "POST":
        user_data = dict()
        nome = request.form.get("inputNome")
        cpf = request.form.get("inputCPF")
        email = request.form.get("inputEmail")
        telefone = request.form.get("inputTelefone")
        user = request.form.get("inputUser")
        senha = request.form.get("inputPassword")
        confirmaSenha = request.form.get("inputPasswordCheck")
        # termos_de_uso = request.form.get("inputCond")

        if senha != confirmaSenha:
            return redirect("/cadastro")

        user_data["nome"] = nome
        user_data["cpf"] = cpf
        user_data["email"] = email
        user_data["telefone"] = telefone
        user_data["usuario"] = user
        user_data["senha"] = senha

        collection_customers.insert_one(parse_json(user_data))

        return user_data
    return redirect("/cadastro")


@app.route("/showEvents/<filter>")
def teste(filter):
    return getEvents(filter)


@app.route("/login")
def signin():
    return render_template("signin.html")


@app.route("/checkUserSignIn", methods=["GET", "POST"])
def checkUserSignIn():
    if request.method == "POST":
        user_data = dict()
        email = request.form.get("inputEmail")
        senha = request.form.get("inputPassword")

        user_data["email"] = email
        user_data["senha"] = senha

        user = collection_customers.find_one({"email": email})
        user = parse_json(user)

        if user["senha"] == senha:
            return redirect("/")
        return redirect("/login")

    return redirect("/login")


if __name__ == '__main__':
    app.run()
