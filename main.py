import bcrypt
from flask import Flask, redirect, render_template, request, url_for, abort
from flask_bcrypt import Bcrypt
from os import urandom
from json import loads
from flask_login import LoginManager, login_user, current_user, user_accessed, login_required, logout_user
from DBconfig import collection_customers, collection_events, parse_json
from bson.objectid import ObjectId
from events_viewer import getEvents
from user_model import User


app = Flask(__name__)

# setup inicial
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = urandom(16)
# mongo = PyMongo(app)


@login_manager.user_loader
def load_user(obj_id):
    user_id = obj_id.replace("'", '"')
    user_id = loads(user_id)
    user_id = user_id["$oid"]
    user = collection_customers.find_one({"_id": ObjectId(user_id)})
    user = parse_json(user)
    if not user:
        return None
    return User(user_json=user)


# routes

@ app.route("/")
def home():
    return render_template("home.html")


@ app.route("/criar_evento")
@login_required
def criar_evento():
    return render_template("creator.html")


@ app.route("/checkNewEvent1", methods=["GET", "POST"])
@login_required
def checkNewEvent1():
    if request.method == "POST":
        event_data = dict()
        titulo = request.form.get("inputTitulo")
        descricao = request.form.get("inputDescricao")
        dia = request.form.get("inputData")
        hora = request.form.get("inputHora")
        categoria = request.form.get("inputCategoria")
        usuario = request.form.get("usuario_criador")

        event_data["titulo"] = titulo
        event_data["descricao"] = descricao
        event_data["dia"] = dia
        event_data["hora"] = hora
        event_data["categoria"] = categoria
        event_data["usuario_criador"] = usuario
        event_data["status"] = "inativo"

        result = collection_events.insert_one(parse_json(event_data))

        print(result.inserted_id)

        return redirect(f"/selecionar_opcoes/{result.inserted_id}")
    return redirect("/criar_evento")


@ app.route("/selecionar_opcoes/<event_id>")
@login_required
def criar_evento2(event_id):
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    event = parse_json(event)
    if event["usuario_criador"] == current_user.id and event["status"] == "inativo":
        return render_template("creator2.html", event_id=event_id, event_name=event["titulo"])
    return "pagina do evento"


@ app.route("/checkNewEvent2/<event_id>", methods=["GET", "POST"])
def checkNewEvent2(event_id):
    if request.method == "POST":
        event_data = request.form.to_dict(flat=False)
        db_event_data = dict()
        odd_init = len(event_data.keys())
        for option in event_data.keys():
            opcao = event_data[option][0]
            db_event_data[f"{opcao}"] = odd_init

        print(db_event_data)

        query = {"_id": ObjectId(event_id)}
        newValues = {"$set": {"opcoes": db_event_data, "status": "ativo"}}

        collection_events.update_one(query, newValues)

        return redirect("/")
    return redirect("/criar_evento")


@ app.route("/cadastro")
def signup():
    return render_template("signup.html")


@ app.route("/checkUserSignUp", methods=["GET", "POST"])
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
        user_data["senha"] = bcrypt.generate_password_hash(
            senha).decode('utf-8')

        user_id = collection_customers.insert_one(parse_json(user_data))

        user_data["_id"] = ObjectId(user_id.inserted_id)
        user = parse_json(user_data)
        user = User(user_json=user)
        login_user(user)

        return redirect(url_for('home'))
    return redirect("/cadastro")


@ app.route("/showEvents/<filter>")
def showEvents(filter):
    return getEvents(filter)


@ app.route("/login")
def signin():
    if current_user.is_authenticated:
        # return redirect(url_for('home'))
        return "esta autenticado"
    return render_template("signin.html")


@ app.route("/checkUserSignIn", methods=["GET", "POST"])
def checkUserSignIn():

    if request.method == "POST":
        user_data = dict()
        email = request.form.get("inputEmail")
        senha = request.form.get("inputPassword")

        user_data["email"] = email
        user_data["senha"] = senha

        user = collection_customers.find_one({"email": email})
        user = parse_json(user)

        # verifica se o usuario existe na base de dados
        if user:
            if bcrypt.check_password_hash(user["senha"], senha):
                user = User(user_json=user)
                login_user(user)

                return redirect(url_for('home'))
            return redirect("/login")
        return "nao existe"
    return redirect("/login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/visualizar_evento/<event_id>")
def event_page(event_id):
    return render_template("event_page.html", event_id=event_id)


@app.route("/get_event_data/<event_id>")
def event_data(event_id):
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    if event == None:
        return redirect(url_for('home'))
    event = parse_json(event)
    return event


if __name__ == '__main__':
    app.run()
