class User():
    def __init__(self, user_json):
        self.id = str(user_json["_id"])
        self.nome = user_json["nome"]
        self.cpf = user_json["cpf"]
        self.email = user_json["email"]
        self.telefone = user_json["telefone"]
        self.usuario = user_json["usuario"]
        self.senha_hash = user_json["senha"]

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id
