from cmath import inf
import bcrypt
from flask import Flask, redirect, render_template, request, url_for, abort, flash
from flask_bcrypt import Bcrypt
from os import urandom
from json import loads
from datetime import datetime
from flask_login import LoginManager, login_user, current_user, user_accessed, login_required, logout_user
from DBconfig import collection_events, collection_customers, parse_json, extract_valid_id, APP_KEY
from bson.objectid import ObjectId
from events_viewer import getEvents
from user_model import User
from odd_calculator import set_init_odd, update_odds


app = Flask(__name__)

# setup inicial

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = APP_KEY



@login_manager.user_loader
def load_user(obj_id):
    user_id = extract_valid_id(obj_id)
    user = collection_customers.find_one({"_id": ObjectId(user_id)})
    user = parse_json(user)
    if not user:
        return None
    return User(user_json=user)


# routes

@ app.route("/")
def home():
    # event = collection_events.find_one({})
    # guests = event['guests']
    # event_id = "630ecaa7028fc75e15d9e4c4"
    # return render_template("tabs.html", guests=guests, nGuests = len(guests), event_id = event_id, event=event)
    # return redirect("/evento/632bbe010c1ace1294ee24f0")
    return render_template("leads.html")


@ app.route("/evento/<event_id>")
def event(event_id):
    
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    guests = event['guests']
    # print(event)
    hasPrice = True
    if len(event['priceOptions']) == 0:
        hasPrice = False

    if current_user.is_authenticated:
        if current_user.is_admin(event['adminUser']):
            print("sou admin")
            return render_template("adminView.html", guests=guests, nGuests = len(guests), event_id = event_id, event=event,hasPrice=hasPrice)
    print("não sou admin")
    return render_template("tabs.html", guests=guests, nGuests = len(guests), event_id = event_id, event=event, hasPrice=hasPrice)


@ app.route("/enquetes/<event_id>")
def pollVote(event_id):
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    return render_template("pollVote.html", polls=event['polls'], event_id=event_id)

@ app.route("/receber-enquetes/<event_id>", methods=["POST"])
def processPoll(event_id):

    polls = request.form.to_dict(flat=True)
    print(polls)
    for poll in polls.keys():
        query = {"_id": ObjectId(event_id), "polls.question": poll}
        newValues = {"$inc": {f"polls.$.options.{int(polls[poll]) - 1 }.numVotes": 1}}
        collection_events.update_one(query, newValues)
    # return "Página de pagamento"
    return redirect(f"/evento/{event_id}")   




@ app.route("/evento/<event_id>/<action>")
def event_action(event_id, action):
    

    if action == 'confirmar':
        if current_user.is_authenticated:
            return redirect(f"/confirmar/{event_id}")
        else:
            return render_template("signin.html", isConfirmAction = True, event_id=event_id)
    elif action == 'talvez':
        event = collection_events.find_one({"_id": ObjectId(event_id)})
        return render_template("maybe.html", guests=event["guests"], event_id=event_id)
    elif action == 'recusar':
        event = collection_events.find_one({"_id": ObjectId(event_id)})
        return render_template("refuse4.html", guests=event["guests"], event_id=event_id)
    
    return redirect(f"/evento/{event_id}")




@ app.route("/confirmar/<event_id>")
def confirm(event_id):
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    return render_template("confirm.html", guests=event["guests"], event_id=event_id)



@ app.route("/recusar/<event_id>", methods=["POST"])
def refuse(event_id):
    
    event = collection_events.find_one({"_id": ObjectId(event_id)})

    if request.method == "POST":
        event_data = dict()
        nome_lista = request.form.get("nome-com-lista")
        nome_avulso = request.form.get("nome-sem-lista")
        if nome_lista == "Selecione seu nome":
            if nome_avulso == '':
                return redirect(f"/evento/{event_id}/recusar")
            else:
                # adicionar o nome recusado na lista
                new_refuse = {"name": nome_avulso, "status": "recusado"}
                query = {"_id": ObjectId(event_id)}
                newValues = {"$push": {"guests": new_refuse}}
                collection_events.update_one(query, newValues)
                return redirect(f"/evento/{event_id}")

        else:
            # new_refuse = {"name": nome_avulso, "status": "recusado"}
            query = {"_id": ObjectId(event_id), "guests.name": nome_lista}
            newValues = {"$set": {"guests.$.status": "recusado"}}
            collection_events.update_one(query, newValues)
            return redirect(f"/evento/{event_id}")
    
    return redirect(f"/evento/{event_id}")



@ app.route("/talvez/<event_id>", methods=["POST"])
def maybe(event_id):
    
    event = collection_events.find_one({"_id": ObjectId(event_id)})

    if request.method == "POST":
        event_data = dict()
        nome_lista = request.form.get("nome-com-lista")
        nome_avulso = request.form.get("nome-sem-lista")
        if nome_lista == "Selecione seu nome":
            if nome_avulso == '':
                return redirect(f"/evento/{event_id}/talvez")
            else:
                # adicionar o nome recusado na lista
                new_refuse = {"name": nome_avulso, "status": "talvez"}
                query = {"_id": ObjectId(event_id)}
                newValues = {"$push": {"guests": new_refuse}}
                collection_events.update_one(query, newValues)
                return redirect(f"/evento/{event_id}")

        else:
            # new_refuse = {"name": nome_avulso, "status": "recusado"}
            query = {"_id": ObjectId(event_id), "guests.name": nome_lista}
            newValues = {"$set": {"guests.$.status": "talvez"}}
            collection_events.update_one(query, newValues)
            return redirect(f"/evento/{event_id}")
    
    return redirect(f"/evento/{event_id}")




@ app.route("/api/evento/<event_id>/polls")
def polls(event_id):
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    eventPolls = parse_json({'polls': event['polls']})
    return eventPolls


@ app.route("/cadastro")
def signup():
    isCreateAction = request.args.get('create', default=False, type=bool)
    isConfirmAction = request.args.get('confirm', default=False, type=bool)
    event_id = request.args.get('event_id')
    return render_template("signup.html", isCreateAction=isCreateAction, isConfirmAction = isConfirmAction, event_id=event_id)


@ app.route("/criar-primeiro-evento")
def firstEvent():
    return render_template("fstEvent.html")


@ app.route("/criar-evento")
def createEvent():
    event_data = dict()
    event_data['address'] = "Endereço do seu evento"
    event_data['eventName'] = "Nome do seu evento"
    event_data['date'] = "Data"
    event_data['time'] = "Horário"
    event_data['description'] = "Descrição"
    event_data['guests'] = []
    event_data['polls'] = []
    event_data['priceOptions'] = []
    event_data['adminUser'] = current_user.id

    event = collection_events.insert_one(parse_json(event_data))

    return redirect(f"/editar-evento/{event.inserted_id}?create=True")



@ app.route("/editar-evento/<event_id>")
def editEvent(event_id):
    # se o usuário for admin do evento
    isCreateAction = request.args.get('create', default=False, type=bool)
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    return render_template("editEvent (1).html", event=event, isCreateAction = isCreateAction)


@ app.route("/editar-convidados/<event_id>")
def editGuests(event_id):
    # se o usuário for admin do evento
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    return render_template("editGuests.html", event=event, guests=event['guests'], nGuests = len(event['guests']))

@ app.route("/editar-precos/<event_id>")
def editPrice(event_id):
    # se o usuário for admin do evento
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    return render_template("editPrice.html", event=event, nPrices = len(event['priceOptions']))


@ app.route("/editar-enquetes/<event_id>")
def editPolls(event_id):
    # se o usuário for admin do evento
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    return render_template("editPolls2.html", event=event, nPolls = len(event['polls']))

@ app.route("/process-event-data/<event_id>", methods=["POST"])
def processEvent(event_id):
    # se o usuário for admin do evento
    if request.method == "POST":
        event_data = dict()
        address = request.form.get("eventAddress")
        eventName = request.form.get("eventName")
        date = request.form.get("eventDate")
        time = request.form.get("eventTime")
        description = request.form.get("eventDescription")

        ano = date[:4]
        mes = date[5:7]
        dia = date[8:]

        date = f"{dia}-{mes}-{ano}"

        event_data['address'] = address
        event_data['eventName'] = eventName
        event_data['date'] = date
        event_data['time'] = time
        event_data['description'] = description


        # retira caixas vazias - criador pode editar uma copisa de cada vez
        event_data_clean = event_data.copy()
        for key in event_data:
            if event_data[key] == '' or event_data[key] == None:
                del event_data_clean[key]


        query = {"_id": ObjectId(event_id)}
        newValues = {"$set": event_data_clean}
        collection_events.update_one(query, newValues)


    return redirect(f"/evento/{event_id}")


@ app.route("/salvar-convidados/<event_id>", methods=["POST"])
def processGuests(event_id):
    # se o usuário for admin do evento
    if request.method == "POST":

        event = collection_events.find_one({"_id": ObjectId(event_id)})
        guests = event["guests"]
        print(guests)
        guest_names = list()
        for guest in guests:
            guest_names.append(guest["name"])

        new_guest_data = request.form.to_dict(flat=False)
        guest_data = list()
        edit_names = list()
        for guest in new_guest_data.values():
            if guest[0] != '':
                guest_data.append({'name': guest[0], 'status': guest[1]})
                edit_names.append(guest[0])


        for guest in guests:
            if guest["name"] not in edit_names:
                guests.remove(guest)



        for guest in guest_data:
            if guest["name"] in guest_names:
                # atualizar status
                for existing in guests:
                    if existing["name"] == guest["name"]:
                        existing["status"] = guest["status"]
            else:
                guests.append(guest)
            
        print(guests)

        db_guest_data = {"guests": guests}

        query = {"_id": ObjectId(event_id)}
        newValues = {"$set": db_guest_data}
        collection_events.update_one(query, newValues)

    return redirect('/editar-evento/' + event_id)



@ app.route("/salvar-precos/<event_id>", methods=["POST"])
def processPrices(event_id):
    # se o usuário for admin do evento
    if request.method == "POST":


        new_price_data = request.form.to_dict(flat=False)
        db_price_data = list()
        is_fst_val = True
        priceOption = dict()
        min_price = 1000000
        for elem in new_price_data.values():
            if is_fst_val:
                priceOption['name'] = elem[0]
                is_fst_val = False
            else:
                if elem[0] == '':
                    priceOption['price'] = 0
                else:
                    priceOption['price'] = int(elem[0])
                is_fst_val = True
                db_price_data.append(priceOption)

                if priceOption['price'] < min_price:
                    min_price = priceOption['price']
                
                priceOption = dict()

        db_price_data = {"priceOptions": db_price_data}

        query = {"_id": ObjectId(event_id)}
        newValues = {"$set": db_price_data}
        collection_events.update_one(query, newValues)

    return redirect('/editar-evento/' + event_id)


@ app.route("/process-confirm/<event_id>", methods=["POST"])
def processConfirm(event_id):

    name = current_user.nome
    userid = current_user.id
    instagram = current_user.instagram
    new_guest = {"name": name, "status": "confirmado", "_id": ObjectId(extract_valid_id(userid)), "instagram": instagram}

    info = request.form.to_dict()

    if "nome-sem-lista" in info.keys():
        # adicionar na lista de convidados
        query = {"_id": ObjectId(event_id)}
        newValues = {"$push": {"guests": new_guest}}
        collection_events.update_one(query, newValues)

    else:
        # encontrar na lista de convidados e substituir
        query = {"_id": ObjectId(event_id), "guests.name": info["nome-com-lista"]}
        newValues = {"$set": {"guests.$": new_guest}}
        collection_events.update_one(query, newValues)
    # redirecionar para as enquertes
    return redirect(f"/enquetes/{event_id}")


@ app.route("/salvar-enquetes/<event_id>", methods=["POST"])
def processPolls(event_id):
    # se o usuário for admin do evento
    if request.method == "POST":

        new_poll_data = request.form.to_dict(flat=False)
        print(new_poll_data)
        db_poll_data = list()
        for poll in new_poll_data.values():
            if poll[0] == '':
                continue
            onePoll = dict()
            options = list()
            onePoll['question'] = poll[0]
            for option in poll[1:]:
                options.append({'optionName': option, 'numVotes':0})
            onePoll['options'] = options
            db_poll_data.append(onePoll)

        # print(db_poll_data)


        db_poll_data = {"polls": db_poll_data}

        query = {"_id": ObjectId(event_id)}
        newValues = {"$set": db_poll_data}
        collection_events.update_one(query, newValues)

    return redirect('/editar-evento/' + event_id)


@ app.route("/logout")
def signout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for("signin"))
    return render_template("signin.html")


@ app.route("/login")
def signin():
    isCreateAction = request.args.get('create', default=False, type=bool)
    isConfirmAction = request.args.get('confirm', default=False, type=bool)

    if current_user.is_authenticated:
        if isCreateAction:
            return redirect(url_for('createEvent'))
        if isConfirmAction:
            event_id = request.args.get('event_id')
            return redirect(f"/confirmar/{event_id}")
        return redirect(url_for('home'))

    if isCreateAction:
        return render_template("signin.html", isCreateAction = True)
    if isConfirmAction:
        event_id = request.args.get('event_id')
        return render_template("signin.html", isConfirmAction = True, event_id=event_id)
    return render_template("signin.html")


@ app.route("/checkUserSignIn", methods=["POST"])
def checkUserSignIn():

    if request.method == "POST":
        user_data = dict()
        email = request.form.get("inputEmail")
        senha = request.form.get("inputPassword")

        user_data["email"] = email
        user_data["senha"] = senha

        user = collection_customers.find_one({"email": email})
        user = parse_json(user)

        isCreateAction = request.args.get('create', default=False, type=bool)
        isConfirmAction = request.args.get('confirm', default=False, type=bool)

        # verifica se o usuario existe na base de dados
        if user:
            if bcrypt.check_password_hash(user["senha"], senha):
                user = User(user_json=user)
                login_user(user)

                print(isCreateAction)
                if isCreateAction:
                    return redirect(url_for('createEvent'))

                if isConfirmAction:
                    event_id = request.args.get('event_id')
                    return redirect(f"/confirmar/{event_id}")

                return redirect(url_for('home'))
            flash('Email ou senha incorreto')
            return redirect(f"/login?create={isCreateAction}&confirm={isConfirmAction}")
        flash('Usuário não encontrado')
        return redirect(f"/login?create={isCreateAction}&confirm={isConfirmAction}")
    return redirect("/login")



@ app.route("/checkUserSignUp", methods=["POST"])
def checkUserSignUp():
    if request.method == "POST":
        user_data = dict()
        nome = request.form.get("userName")
        email = request.form.get("userEmail")
        telefone = request.form.get("userPhone")
        insta = request.form.get("userInstagram")
        senha = request.form.get("userPassword")
        confirmaSenha = request.form.get("userPasswordCheck")
        # termos_de_uso = request.form.get("inputCond")

        isCreateAction = request.args.get('create', default=False, type=bool)
        isConfirmAction = request.args.get('confirm', default=False, type=bool)
        event_id = request.args.get('event_id')

        if senha != confirmaSenha:
            return redirect("/cadastro")

        user_data["nome"] = nome
        user_data["email"] = email
        user_data["telefone"] = telefone
        if insta == '':
            user_data["instagram"] = "Insta não informado"
        else:
            user_data["instagram"] = f"@{insta}"
        user_data["senha"] = bcrypt.generate_password_hash(
            senha).decode('utf-8')
        user_data["eventos"] = []

        user_id = collection_customers.insert_one(parse_json(user_data))

        # user_data["_id"] = ObjectId(user_id.inserted_id)
        # user = parse_json(user_data)
        # user = User(user_json=user)
        # login_user(user)

        return render_template("signin.html", isCreateAction=isCreateAction, isConfirmAction=isConfirmAction, event_id=event_id)
    return redirect("/cadastro")


# @ app.route("/criar_evento")
# @login_required
# def criar_evento():
#     return render_template("creator.html")


# @ app.route("/checkNewEvent1", methods=["GET", "POST"])
# @login_required
# def checkNewEvent1():
#     if request.method == "POST":
#         event_data = dict()
#         titulo = request.form.get("inputTitulo")
#         descricao = request.form.get("inputDescricao")
#         dia = request.form.get("inputData")
#         hora = request.form.get("inputHora")
#         categoria = request.form.get("inputCategoria")
#         usuario = request.form.get("usuario_criador")
#         data_atual = datetime.now()

#         event_data["titulo"] = titulo
#         event_data["descricao"] = descricao
#         event_data["dia-termino"] = dia
#         event_data["hora-termino"] = hora
#         event_data["categoria"] = categoria
#         event_data["usuario_criador"] = ObjectId(extract_valid_id(usuario))
#         event_data["status"] = "inativo"
#         event_data["data-criacao"] = data_atual

#         result = collection_events.insert_one(parse_json(event_data))

#         # ataulizando usuário
#         query = {"_id": event_data["usuario_criador"]}
#         newValues = {
#             "$push": {"eventos-criados": ObjectId(result.inserted_id)}}
#         collection_customers.update_one(query, newValues)

#         print(result.inserted_id)

#         return redirect(f"/selecionar_opcoes/{result.inserted_id}")
#     return redirect("/criar_evento")


# @ app.route("/selecionar_opcoes/<event_id>")
# @login_required
# def criar_evento2(event_id):
#     event = collection_events.find_one({"_id": ObjectId(event_id)})
#     event = parse_json(event)
#     if str(event["usuario_criador"]) == current_user.id and event["status"] == "inativo":
#         return render_template("creator2.html", event_id=event_id, event_name=event["titulo"])
#     return redirect(url_for("event_page", event_id=event_id))


# @ app.route("/checkNewEvent2/<event_id>", methods=["GET", "POST"])
# def checkNewEvent2(event_id):
#     if request.method == "POST":
#         new_event_data = request.form.to_dict(flat=False)
#         db_event_data = dict()
#         nOpcoes = len(new_event_data.keys())
#         for option in new_event_data.keys():
#             opcao = new_event_data[option][0]
#             db_event_data[f"{opcao}"] = {
#                 "odd": set_init_odd(nOpcoes), "aportes": []}

#         # print(db_event_data)

#         query = {"_id": ObjectId(event_id)}
#         newValues = {"$set": {"opcoes": db_event_data, "status": "ativo"}}

#         collection_events.update_one(query, newValues)

#         return redirect("/")
#     return redirect("/criar_evento")



# @ app.route("/checkUserSignUp", methods=["GET", "POST"])
# def checkUserSignUp():
#     if request.method == "POST":
#         user_data = dict()
#         nome = request.form.get("inputNome")
#         cpf = request.form.get("inputCPF")
#         email = request.form.get("inputEmail")
#         telefone = request.form.get("inputTelefone")
#         user = request.form.get("inputUser")
#         senha = request.form.get("inputPassword")
#         confirmaSenha = request.form.get("inputPasswordCheck")
#         # termos_de_uso = request.form.get("inputCond")

#         if senha != confirmaSenha:
#             return redirect("/cadastro")

#         user_data["nome"] = nome
#         user_data["cpf"] = cpf
#         user_data["email"] = email
#         user_data["telefone"] = telefone
#         user_data["usuario"] = user
#         user_data["senha"] = bcrypt.generate_password_hash(
#             senha).decode('utf-8')
#         user_data["eventos-aportados"] = []
#         user_data["saldo"] = 100.0

#         user_id = collection_customers.insert_one(parse_json(user_data))

#         user_data["_id"] = ObjectId(user_id.inserted_id)
#         user = parse_json(user_data)
#         user = User(user_json=user)
#         login_user(user)

#         return redirect(url_for('home'))
#     return redirect("/cadastro")


# @ app.route("/showEvents")
# def showEvents():
#     filters = request.args.to_dict()
#     print(filters)
#     if current_user.is_authenticated:
#         return getEvents(filters, current_user.id)
#     return getEvents(filters)





# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("home"))


# @app.route("/visualizar_evento/<event_id>")
# def event_page(event_id):
#     event = collection_events.find_one({"_id": ObjectId(event_id)})
#     if event == None:
#         return redirect(url_for('home'))

#     # descomentar para a visualização doc riador
#     # if current_user.is_authenticated and event["usuario_criador"]["$oid"] == extract_valid_id(current_user.id):
#     #     return render_template("creator_view.html")

#     args = request.args.to_dict()
#     if "option" in args:
#         return render_template("event_page.html", event_id=event_id, option=args["option"])
#     return render_template("event_page.html", event_id=event_id)


# @app.route("/get_event_data/<event_id>")
# def event_data(event_id):
#     event = collection_events.find_one({"_id": ObjectId(event_id)})
#     event = parse_json(event)
#     return event


# @app.route("/process_bet/<event_id>", methods=["GET", "POST"])
# @login_required
# def process_bet(event_id):
#     if request.method == "POST":

#         # atualizando coleção de eventos
#         usuario = ObjectId(extract_valid_id(current_user.id))
#         valor = request.form.get("valor_apostado")
#         opcao = request.form.get("options")
#         horario = datetime.now()
#         odd_do_aporte = request.form.get("odd-da-compra")

#         bet_data = dict()
#         bet_data["usuario"] = usuario
#         bet_data["valor-aporte"] = float(valor)
#         bet_data["horario"] = horario
#         bet_data["odd-comprada"] = round(float(odd_do_aporte), 2)

#         query = {"_id": ObjectId(event_id)}
#         newValues = {"$push": {f"opcoes.{opcao}.aportes": bet_data}}

#         collection_events.update_one(query, newValues)

#         # atualizando coleção de usuários
#         query2 = {"_id": ObjectId(extract_valid_id(current_user.id))}
#         user = collection_customers.find_one(query2)

#         if ObjectId(event_id) not in user["eventos-aportados"]:

#             newValues2 = {"$push": {"eventos-aportados": ObjectId(event_id)}}
#             collection_customers.update_one(query2, newValues2)

#         update_odds(event_id)

#         return redirect(url_for("home"))
#     return redirect(url_for("home"))


# @ app.route("/perfil")
# @login_required
# def perfil():
#     return render_template("user_profile.html")


# @ app.route("/alterar_dados")
# @login_required
# def alterar_dados():
#     return render_template("update_user_data.html")


# @ app.route("/checkUserDataUpdate", methods=["GET", "POST"])
# @login_required
# def checkUserDataUpdate():
#     if request.method == "POST":
#         user_data = dict()
#         nome = request.form.get("inputNome")
#         cpf = request.form.get("inputCPF")
#         email = request.form.get("inputEmail")
#         telefone = request.form.get("inputTelefone")
#         user = request.form.get("inputUser")

#         user_data["nome"] = nome
#         user_data["cpf"] = cpf
#         user_data["email"] = email
#         user_data["telefone"] = telefone
#         user_data["usuario"] = user

#         query = {"_id": ObjectId(extract_valid_id(current_user.id))}
#         newValues = {"$set": user_data}

#         collection_customers.update_one(query, newValues)

#         return redirect(url_for('home'))
#     return redirect("/cadastro")


# @ app.route("/gerenciar_eventos")
# @login_required
# def creator_page():
#     # if usuario é criador:
#     return render_template("creator_page.html")


if __name__ == '__main__':
    app.run(debug=True)
