import vk_api

from modules.c_access_token import AccessT
from modules.oth_function import path

login_data = {
    "token": "",
    "login": "",
    "password": ""}


# Отвечает за авторизацию
class LoginVK:
    API_VERSION = '5.92'

    def __init__(self, self_login_data):
        self.login_data = self_login_data
        self.access_token = ""
        self.name = ""
        self.own_id = 0
        self.vk = None
        self.account = None
        self.login_vks()

    def login_vks(self):
        try:
            if 'token' in self.login_data and self.login_data['token']:
                token = self.login_data['token']
                vk_session = vk_api.VkApi(token=token, auth_handler=self.auth_handler)
            elif 'login' in self.login_data and 'password' in self.login_data:
                login, password = self.login_data['login'], self.login_data['password']
                vk_session = vk_api.VkApi(login, password, captcha_handler=self.captcha_handler,
                                          api_version=LoginVK.API_VERSION, auth_handler=self.auth_handler,
                                          scope="65536", app_id=2685278)
                vk_session.auth(token_only=True, reauth=True)
            else:
                raise KeyError('Введите токен или логин-пароль')

            self.access_token = vk_session.token['access_token']
            self.vk = vk_session.get_api()
            self.account = self.vk.account.getProfileInfo()

            if self.account["id"] > 0:
                self.name = f'{self.account["first_name"]} {self.account["last_name"]}'
                self.own_id = self.account["id"]
            else:
                raise Exception

        except Exception as e:
            if not self.login_data['token'] == "":
                AccessT().remove_token(self.login_data['token'])
            raise ConnectionError(e)

    # Выводит кто авторизован
    def auth_print(self):
        try:
            print(f'{self.name} -  Авторизован\n')
        except Exception as e:
            from modules import c_error
            c_error.add_error(e)

    @staticmethod
    def auth_handler():
        key = input('Введите код двухфакторой аутентификации: ').strip()
        remember_device = True
        return key, remember_device

    @staticmethod
    def captcha_handler(captcha):
        key = input(f"Введите капчу ({captcha.get_url()}): ").strip()
        return captcha.try_again(key)


def clean_login_data():
    global login_data
    login_data = {
        "token": "",
        "login": "",
        "password": ""}


# val1 - dump_path
# val2 - user own_id
# val3 - user name
def set_path_user(val1: str, val2: str, val3: str):
    return f'{path}/{val1}/{val2} - {val3}'
