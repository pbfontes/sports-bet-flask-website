from DBconfig import collection_events
from bson.objectid import ObjectId


def get_odd(prob, heik=0.2):
    return (1 / prob) * (1 - heik)


def set_init_odd(nOpcoes):
    return get_odd(1/nOpcoes)


def get_total_bet(option_values):
    ''' retorna o aporte total um uma certa opção a partir do valor da opcao'''

    soma = 0
    for aporte in option_values["aportes"]:
        soma += aporte["valor-aporte"]
    return soma


def get_bet_list(event):
    bet_list = list()
    for option in event["opcoes"].values():
        bet_list.append(get_total_bet(option))
    return bet_list


def get_prob_list(bet_list):
    prob_list = list()
    tam_ajuste = 100
    total_bet = sum(bet_list) + tam_ajuste
    ajuste = tam_ajuste/len(bet_list)
    for option in bet_list:
        prob_list.append((option + ajuste)/total_bet)
    return prob_list


def update_odds(event_id):

    query = {"_id": ObjectId(event_id)}
    event = collection_events.find_one(query)

    bet_list = get_bet_list(event)
    prob_list = get_prob_list(bet_list)

    odd_data = dict()
    for i, option in enumerate(event["opcoes"]):
        odd_data[f"opcoes.{option}.odd"] = get_odd(prob=prob_list[i])

    print(odd_data)
    newValues = {"$set": odd_data}

    collection_events.update_one(query, newValues)
