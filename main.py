from flask import Flask, redirect, render_template, request
from DBconfig import collection, parse_json

app = Flask(__name__)


@app.route("/")
def home():
    # x = collection.find_one()
    # x1 = x["name"]
    # x2 = x["address"]
    # f"<h1>{x1}, {x2}</h1>"
    return render_template("home.html")


@app.route("/cadastro")
def signup():
    return render_template("signup.html")


@app.route("/checkUserInput", methods=["GET", "POST"])
def checkUserInput():
    if request.method == "POST":
        user_data = dict()
        nome = request.form.get("inputNome")
        cpf = request.form.get("inputCPF")
        email = request.form.get("inputEmail")
        telefone = request.form.get("inputTelefone")
        user = request.form.get("inputUser")
        senha = request.form.get("inputPassword")
        confirmaSenha = request.form.get("inputPasswordCheck")
        termos_de_uso = request.form.get("inputCond")

        if senha != confirmaSenha:
            return redirect("/cadastro")

        if termos_de_uso == None:
            return redirect("/cadastro")

        user_data["nome"] = nome
        user_data["cpf"] = cpf
        user_data["email"] = email
        user_data["telefone"] = telefone
        user_data["usuario"] = user
        user_data["senha"] = senha

        collection.insert_one(parse_json(user_data))

        return user_data
    return redirect("/cadastro")


if __name__ == '__main__':
    app.run()
