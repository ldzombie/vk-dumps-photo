import time

import vk_api

from modules import menus, c_access_token
from modules.Strings import Texts
from modules.config import bot
from vk.modules.oth_function import path

from modules.c_access_token import remove_token

login_data = {
    "token": "",
    "login": "",
    "password": "",
    "chat_id": 0}

key = None
capt = None

def auth_handler():
    remember_device = True

    msg = bot.send_message(int(login_data['chat_id']), Texts['w_two_auth_code'])
    bot.register_next_step_handler(msg, auth_han)
    while True:
        if key is None:
            time.sleep(3)
        else:
            break

    return key, remember_device


def captcha_handler(captcha):
    print("Capt")

    msg = bot.send_photo(int(login_data['chat_id']), photo=captcha.get_image())
    bot.register_next_step_handler(msg, auth_cap, captcha)

    while True:
        if capt is None:
            time.sleep(5)
        else:
            break
    return captcha.try_again(capt)


# Отвечает за авторизацию
class LoginVK:
    API_VERSION = '5.92'

    def __init__(self, self_login_data, user_id):
        self.login_data = self_login_data
        self.access_token = ""
        self.name = ""
        self.own_id = 0
        self.user_id = user_id
        self.vk = None
        self.account = None
        self.login_vks()

    def login_vks(self):
        try:
            global key
            global capt
            key = None
            capt = None
            if 'token' in self.login_data and self.login_data['token']:
                token = self.login_data['token']
                vk_session = vk_api.VkApi(token=token, auth_handler=auth_handler)
            elif 'login' in self.login_data and 'password' in self.login_data:
                login, password = self.login_data['login'], self.login_data['password']
                vk_session = vk_api.VkApi(login, password, captcha_handler=captcha_handler,
                                          api_version=LoginVK.API_VERSION, auth_handler=auth_handler,
                                          scope="65536", app_id=2685278)
                vk_session.auth(token_only=True, reauth=True)

            self.access_token = vk_session.token['access_token']
            self.vk = vk_session.get_api()
            self.account = self.vk.account.getProfileInfo()

            if self.account["id"] > 0:
                self.name = f'{self.account["first_name"]} {self.account["last_name"]}'
                self.own_id = self.account["id"]

                c_access_token.none_or_create(self.user_id, self.name, self.access_token)

                bot.send_message(login_data['chat_id'], Texts['auth_info'].format(self.name),
                                 parse_mode='html', reply_markup=menus.m_main())

            else:
                raise Exception

        except Exception as e:
            if not self.login_data['token'] == "":
                remove_token(self.login_data['token'])
            print(e)
            bot.send_message(login_data['chat_id'], Texts['auth_failed'], reply_markup=menus.start_inline_menu())


def clean_login_data():
    global login_data
    login_data = {
        "token": "",
        "login": "",
        "password": "",
        "chat_id": 0}


def auth_han(message):
    global key
    key = message.text.strip()


def auth_cap(message, captcha):
    global capt
    capt = message.text.strip()


# val1 - dump_path
# val2 - user own_id
# val3 - user name
def set_path_user(user_id, val1: str, val2: str, val3: str):
    return f'{path}/{user_id}/{val1}/{val2} - {val3}'
