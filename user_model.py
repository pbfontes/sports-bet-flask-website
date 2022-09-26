class User():
    def __init__(self, user_json):
        self.id = str(user_json["_id"])
        self.nome = user_json["nome"]
        self.email = user_json["email"]
        self.telefone = user_json["telefone"]
        self.instagram = user_json["instagram"]
        self.senha_hash = user_json["senha"]
        self.events = user_json["eventos"]

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

    def is_admin(self, admin_id):
        return self.id == admin_id