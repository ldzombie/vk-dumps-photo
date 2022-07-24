from os.path import join, exists
import json


# Класс отвечающий за управление данными сохраненых пользователей
class AccessT:
    auth_vks = {"users": []}
    name_file = "auth_vk.json"

    def __init__(self):
        if exists(self.name_file):
            with open(self.name_file, 'r') as file:
                self.auth_vks = json.load(file)

    def dump(self):
        with open(self.name_file, 'w+') as file:
            json.dump(self.auth_vks, file)

    def contains(self, lis, fil):
        for x in lis:
            if fil(x):
                return True
        return False

    def add(self, user: list[str, str]):
        if not self.contains(self.auth_vks["users"], lambda x: x['access_token'] == user['access_token']):
            self.auth_vks["users"].append(user)
            self.dump()

    def remove(self, user: list[str, str]):
        if self.contains(self.auth_vks["users"], lambda x: x['access_token'] == user['access_token']):
            self.auth_vks["users"].remove(user)
            self.dump()

    def remove_token(self, val1: str):
        for i in self.auth_vks["users"]:
            if i['access_token'] == val1:
                self.auth_vks["users"].remove(i)
                self.dump()

    def get_token_id(self, index: int):
        return self.auth_vks["users"][index]["access_token"]

    def length(self):
        return len(self.auth_vks["users"])

    def get_users(self):
        print("\nРанее авторизованные: ")
        for index, user in enumerate(self.auth_vks["users"]):
            print(f"{index} - {user['name']}")
