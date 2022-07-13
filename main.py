import vk_api
import os
import json
from os import makedirs
from os.path import join, exists
import base64
import requests
import sys
import argparse
from art import tprint
import time

path, filename = os.path.split(os.path.abspath(__file__))


def clear():
    os.system('cls')


login_data = {
    "token": "",
    "login": "",
    "password": ""}

# globals
limit_dialog = 0
limit_photo = 0
dump_txt = False
dump_html = True
dump_html_offline = False
path_user = ""

login_vk = None
setting = None

name = ""
own_id = 0


class ErrorLog:
    def __init__(self):
        self.errors = []

    def add(self, module, error):
        self.errors.append(f'{module} - {error}')

    def error_list(self):
        return self.errors

    def save_log(self, log_file='errors.log'):
        if self.errors and log_file:
            with open(log_file, 'w') as error_log_file:
                for error in self.errors:
                    error_log_file.write(f'{error}\n')


error_log = ErrorLog()


# Отвечает за авторизацию
class LoginVK:
    API_VERSION = '5.92'

    def __init__(self, self_login_data):
        self.login_data = self_login_data
        self.access_token = ""
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
        except Exception as e:
            raise ConnectionError(e)

    @staticmethod
    def auth_handler():
        key = input('Введите код двухфакторой аутентификации: ').strip()
        remember_device = True
        return key, remember_device

    @staticmethod
    def captcha_handler(captcha):
        key = input(f"Введите капчу ({captcha.get_url()}): ").strip()
        return captcha.try_again(key)


# Класс всех настроек
class Settings:
    def_config = {
        "setting": {
            "path": "dump",
            "download": False,
            "dump_txt": False,
            "dump_html": True,
            "dump_html_offline": False,
            "limit_photo": 1000,
            "limit_dialog": 50
        }}

    def __init__(self):
        self.dump_path = None
        self.limits = [5000, 1000]  # 1 -  лимит фото из диалога 2 - лимит диалогов
        try:
            with open('config.json', 'r') as config_file:
                self.def_config = json.load(config_file)
        # auth_menu()
        except Exception as e:
            if "No such file or directory" in str(e):
                self.dump_config()
            # auth_menu()
            error_log.add("Settings __init__", e)

    def dump_config(self):
        try:
            with open('config.json', 'w') as config_file:
                json.dump(self.def_config, config_file)
        except Exception as e:
            error_log.add("Settings dump", e)

    def get_dump_config(self):
        global limit_dialog
        global limit_photo
        # global download
        global dump_txt
        global dump_html
        global dump_html_offline
        global path_user

        self.dump_path = self.def_config['setting']['path']

        limit_photo = self.def_config['setting']['limit_photo']
        limit_dialog = self.def_config['setting']['limit_dialog']
        # download = self.def_config['setting']['download']
        dump_txt = self.def_config['setting']['dump_txt']
        dump_html = self.def_config['setting']['dump_html']
        dump_html_offline = self.def_config['setting']['dump_html_offline']
        path_user = f'{path}/{self.dump_path}/{own_id} - {name}'
        makedirs(path_user, exist_ok=True)

    def update_settings(self, bol: bool):
        try:
            self.dump_config()
            self.get_dump_config()
            if bol:
                menu_settings()
        except Exception as e:
            error_log.add("update_settings", e)

    def check_err(self):
        if not dump_txt and not dump_html and not dump_html_offline: # and not download
            self.def_config['setting']['dump_html'] = True
        if limit_photo > self.limits[0]:
            self.def_config['setting']['limit_photo'] = self.limits[0]
        if limit_dialog > self.limits[1]:
            self.def_config['setting']['limit_dialog'] = self.limits[1]
        if not self.dump_path:
            self.def_config['setting']['path'] = "dump"
        self.update_settings(False)

    # def set_download(self, b, bol=True):
    #     self.def_config['setting']['download'] = b
    #     self.update_settings(bol)

    def set_dump(self, key: str, b: bool, bol=True):
        self.def_config['setting'][key] = b
        self.update_settings(bol)

    def set_limit_photo(self, b: int, bol=True):
        if b > self.limits[0]:
            menu_settings("слишком большое число")
        else:
            self.def_config['setting']['limit_photo'] = b
            self.update_settings(bol)

    def set_limit_dialog(self, b: int, bol=True):
        if b > self.limits[1]:
            menu_settings("слишком большое число")
        else:
            self.def_config['setting']['limit_dialog'] = b
            self.update_settings(bol)

    def set_dump_path(self, b: str, bol=True):
        self.def_config['setting']['path'] = b
        self.update_settings(bol)


# Класс отвечающий за управление данными сохраненых пользователей
class AccessT:
    auth_vks = {"users": []}
    name_file = "auth_vk.json"

    def __init__(self):
        if exists(self.name_file):
            with open(self.name_file, 'r') as file:
                self.auth_vks = json.load(file)

    def dump(self):
        try:
            with open('auth_vk.json', 'w') as file:
                json.dump(self.auth_vks, file)
        except Exception as e:
            error_log.add("Access dump", e)

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

    def get_token_id(self, index: int):
        return self.auth_vks["users"][index]["access_token"]

    def length(self):
        return len(self.auth_vks["users"])


# Фотографии из диалогов
def get_dialogs_photo(p_id: int, hide: bool = False):
    try:
        if dump_html or dump_html_offline:
            imgs = ""
        if dump_txt:
            urls = []
            dialogs = []
        if p_id > 0:
            test = login_vk.vk.messages.getConversationsById(peer_ids=p_id)
            all_dialogs = test["items"]
        else:
            if limit_dialog == 0 or limit_dialog > 200:
                test = login_vk.vk.messages.getConversations(count=200)  # Получаем диалоги через токен
                all_dialogs = test["items"]

                if len(all_dialogs) == 200:
                    # Нужно чтобы получить все диалоги, если их больше 200
                    offset = 200  # сдвиг начала отсчёта
                    while True:
                        fo1 = login_vk.vk.messages.getConversations(count=200, offset=offset)
                        length = len(fo1["items"])

                        if length > 0:
                            all_dialogs += fo1["items"]
                        else:
                            break
                        if length == 200:
                            offset += 200
                        else:
                            break
            else:
                all_dialogs = login_vk.vk.messages.getConversations(count=limit_dialog)["items"]

        num = len(all_dialogs)
        # Количество диалогов
        print(f"Всего найдено диалогов: {num}")
        print(f"Начинаю выгрузку фотографий | {name} - vk.com/id{own_id}")

        path_dialog = f'{path_user}/dialog'



        for dialog in all_dialogs:  # Идем по списку
            if p_id > 0:
                idd = dialog["peer"]["id"]
                peer_type = dialog['peer']['type']  # Информация о диалоге
            else:
                idd = dialog["conversation"]["peer"]["id"]  # Вытаскиваем ID человека с  диалога
                peer_type = dialog['conversation']['peer']['type']  # Информация о диалоге (конференция это или человек)

            if peer_type == "user":  # Ставим проверку конференции
                if idd > 0:  # Ставим проверку на группы

                    b = login_vk.vk.users.get(user_ids=idd)[0]  # Получаем информацию о человеке

                    fio = f'{b["first_name"]} {b["last_name"]}'

                    print(f"Выгрузка фотографий - {idd} - {fio}")

                    if limit_photo <= 200 and not limit_photo == 0:
                        fo = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo', start_from=0,
                                                                        count=limit_photo,
                                                                        preserve_order=1, max_forwards_level=45)
                        a_photo = fo["items"]

                    else:
                        fo = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo', start_from=0,
                                                                        count=200,
                                                                        preserve_order=1, max_forwards_level=45)
                        a_photo = fo["items"]

                        if len(a_photo) == 200:
                            offset = fo["next_from"]  # сдвиг начала отсчёта
                            while True:
                                if limit_photo == 0:
                                    count = 200
                                else:
                                    count = limit_photo - len(a_photo)
                                    if count >= 200:
                                        count = 200
                                    if count == 0 or count < 0:
                                        break
                                fo1 = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo',
                                                                                 start_from={offset},
                                                                                 count=count,
                                                                                 preserve_order=1,
                                                                                 max_forwards_level=45)
                                length = len(fo1["items"])
                                if length > 0:
                                    a_photo += fo1["items"]
                                else:
                                    break
                                length_all = len(a_photo)
                                # Проверка на то нужно ли делать ещё один цикл, и не превышает ли число фотографий лимит
                                if length == 200 and length_all < limit_photo or length == 200 and limit_photo == 0:
                                    offset = fo1["next_from"]
                                else:
                                    break

                    if len(a_photo) == 0:
                        continue

                    for i in a_photo:  # Идем по списку вложений
                        for j in i["attachment"]["photo"]["sizes"]:
                            if 500 < j["height"] < 650:  # Проверка размеров
                                url = j["url"]  # Получаем ссылку на изображение
                                if dump_txt:
                                    urls.append(url)
                                if dump_html and not dump_html_offline:
                                    imgs += f'<img class="photos" src="{url}" alt="Не удалось загрузить" ' \
                                            f'title="Найдено в диалоге - vk.com/id{idd}">'  # Сохраняем в переменную
                                if dump_html_offline:
                                    base = get_as_base64(url)
                                    imgs += f'<img class="photos" src="data:image/png;base64,{base}" ' \
                                            f'alt="Не удалось загрузить " title="Найдено в альбоме - {idd}">'
                                break  # чтобы не сохраняло одинаковые фотографии разного размера
                    if dump_html or dump_html_offline:
                        try:
                            makedirs(f'{path_dialog}', exist_ok=True)
                            with (open(f'{path_dialog}/{idd} - {fio}.html', 'w+', encoding="utf8") as save_photo,
                                  open(f'{path}/photo_pre.html', 'r', encoding="utf8") as photo_pre):
                                save_photo.write(photo_pre.read() + imgs)
                        except Exception as e:
                            error_log.add("get_dialogs_photo save_photo", e)

                        imgs = ""
                    if dump_txt:
                        dialogs.append({'name': '_'.join(fio), 'photos': urls})
                        urls = []
                    c_text("green", f"[+]Выгруженно {len(a_photo)} фотографий")
                else:
                    print("Это группа!")
            else:
                print("Это конфа!")

        if dump_txt:
            if p_id > 0:
                file_name = f'{idd} - {fio}.json'
            else:
                file_name = 'dialogs.json'
                
            with open(join(f'{path_dialog}', file_name), 'w') as alb_file:
                json.dump(dialogs, alb_file)

        c_text("purple", "\nВыгрузка фотографий из диалогов завершена")
        if not hide:
            out_dump()
    except Exception as e:  # Исключения ошибок
        error_log.add('get_dialogs_photo', e)
        print(e)
        if not hide:
            out_dump()


# Фотографии из плейлистов пользователя по id
def get_photos_friend(user_id: int, onlySaved: bool = True, hide: bool = False):
    try:
        if user_id == 0:
            user_id = own_id
            path_albums = f'{path_user}/albums'
        else:
            user = login_vk.vk.users.get(user_ids=user_id)[0]
            fio = f'{user["first_name"]} {user["last_name"]}'
            path_user_friend = f'{path}/dump/{user_id} - {fio}'
            path_albums = f'{path_user_friend}/albums'

        if onlySaved:
            albums = login_vk.vk.photos.getAlbums(owner_id=user_id, album_ids="-15")
        else:
            albums = login_vk.vk.photos.getAlbums(owner_id=user_id, need_system=1)

        num = albums["count"]  # Количество альбомов

        print(f"Всего найдено альбомов: {num}")

        if num == 0:
            raise Exception

        print(f"Начинаю выгрузку фотографий")


        if dump_html or dump_html_offline:
            imgs = ""
        if dump_txt:
            json_albums = []
            urls = []

        for album in albums["items"]:
            idd = album["id"]
            title = album["title"]
            size = album["size"]
            if size == 0:
                continue

            print(f"{title} - Фото: {size}")

            a_photos = get_album_photo(user_id, idd, size)

            for i in a_photos:  # Идем по списку вложений
                for j in i["sizes"]:
                    if 500 < j["height"] < 650:  # Проверка размеров
                        url = j["url"]  # Получаем ссылку на изображение
                        if dump_txt:
                            urls.append(url)
                        if dump_html and not dump_html_offline:
                            imgs += f'<img class="photos" src="{url}" alt="Не удалось загрузить" ' \
                                    f'title="Найдено в альбоме - {idd}">'  # Сохраняем в переменную
                        if dump_html_offline:
                            base = get_as_base64(url)
                            imgs += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось загрузить" ' \
                                    f'title="Найдено в альбоме - {idd}">'
                        break  # чтобы не добавляло одинаковых фото
            if dump_txt:
                json_albums.append({'name': "_".join(title.split(' ')), 'photos': urls})

            c_text("green", f"[+]Выгруженно {len(a_photos)} фотографий")
            if dump_html or dump_html_offline:
                try:
                    makedirs(f'{path_albums}', exist_ok=True)
                    with (open(f'{path_albums}/{title}.html', 'w+', encoding="utf8") as save_photo,
                          open(f'{path}/photo_pre.html', 'r', encoding="utf8") as photo_pre):
                        save_photo.write(photo_pre.read() + imgs)
                except Exception as e:
                    error_log.add("get_photos_friend save_photo", e)

        if dump_txt:
            with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                json.dump(json_albums, alb_file)
        c_text("purple", "\nВыгрузка фотографий из альбомов завершена")
        if not hide:
            out_dump()
    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friend', e)
        print(e)
        if not hide:
            out_dump()


# Фотографии из плейлистов друзей с открытыми сохрами
def get_photos_friends(onlySaved: bool = True, hide: bool = False):
    try:
        friends = login_vk.vk.friends.get(fields="1", order="hints", name_case="nom", count=250)
        print("Общее количество пользователей: " + str(friends['count']))
        for friend in friends['items']:
            friend_id = friend['id']
            try:
                if onlySaved:
                    albums = login_vk.vk.photos.getAlbums(owner_id=friend_id, album_ids="-15")
                    if not albums['items'][0]['id'] == -15:
                        continue
                else:
                    albums = login_vk.vk.photos.getAlbums(owner_id=friend_id, need_system=1)
                if albums['count'] == 0:
                    continue
            except Exception:
                continue

            if dump_txt:
                json_albums = []
                urls = []
            if dump_html or dump_html_offline:
                imgs = ""

            fio = f'{friend["first_name"]} {friend["last_name"]}'

            print(f"Начинаю выгрузку фотографий " + fio)
            path_user_friend = f'{path}/dump/{friend_id} - {fio}'
            path_albums = f'{path_user_friend}/albums'


            idd = albums['items'][0]['id']
            title = albums['items'][0]["title"]
            size = albums['items'][0]["size"]
            print(f"{title} - Фото: {size}")

            a_photos = get_album_photo(friend_id, idd, size)

            for i in a_photos:  # Идем по списку вложений
                for j in i["sizes"]:
                    if 500 < j["height"] < 650:  # Проверка размеров
                        url = j["url"]  # Получаем ссылку на изображение
                        if dump_txt:
                            urls.append(url)
                        if dump_html and not dump_html_offline:
                            imgs += f'<img class="photos" src="{url}" alt="Не удалось загрузить" ' \
                                    f'title="Найдено в альбоме - {idd}">'  # Сохраняем в переменную
                        if dump_html_offline:
                            base = get_as_base64(url)
                            imgs += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось загрузить" ' \
                                    f'title="Найдено в альбоме - {idd}">'
                        break  # чтобы не добавляло одинаковых фото
            if dump_txt:
                json_albums.append({'name': "_".join(title.split(' ')), 'photos': urls})
            c_text("green", f"[+]Выгруженно {len(a_photos)} фотографий")
            if dump_html or dump_html_offline:
                try:
                    makedirs(f'{path_user_friend}/albums', exist_ok=True)
                    with (open(f'{path_albums}/{title}.html', 'w+', encoding="utf8") as save_photo,
                          open(f'{path}/photo_pre.html', 'r', encoding="utf8") as photo_pre):
                        save_photo.write(photo_pre.read() + imgs)
                except Exception as e:
                    error_log.add("get_photos_friends save_photo", e)

            if dump_txt:
                with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                    json.dump(json_albums, alb_file)
        c_text("purple", "\nВыгрузка фотографий из альбома завершена")
        if not hide:
            out_dump()

    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friends', e)
        print(e)
        if not hide:
            out_dump()


# Метод для получения всех фотографий из альбома
def get_album_photo(user_id: int, album_id: int, siz: int) -> list:
    if limit_photo == 0 or limit_photo > 1000:
        al_photos = login_vk.vk.photos.get(owner_id=user_id,
                                           album_id=album_id,
                                           photo_sizes=1,
                                           rev=1,
                                           count=1000,
                                           offset=0)["items"]
        if len(al_photos) == 1000:
            if siz > 4000:  # Количество фото в альбоме
                siz = 4000
            while True:  # получаем все фотографии если их больше 1000
                offset = 1000  # сдвиг начала отсчёта
                if limit_photo == 0:
                    count = siz - len(al_photos)
                else:
                    count = limit_photo - len(al_photos)
                    if count <= 0:
                        break
                if count > 1000:
                    count = 1000
                time.sleep(1)
                fo1 = login_vk.vk.photos.get(owner_id=user_id,
                                             album_id=album_id,
                                             photo_sizes=1,
                                             rev=1,
                                             count=count,
                                             offset=offset)["items"]
                length = len(fo1)
                if length > 0:
                    al_photos += fo1
                else:
                    break
                if len(al_photos) < siz and (len(al_photos) < limit_photo or limit_photo == 0):
                    offset += 1000
                else:
                    break
    else:
        al_photos = login_vk.vk.photos.get(owner_id=user_id,
                                           album_id=album_id,
                                           photo_sizes=1,
                                           rev=1,
                                           count=1000)["items"]
    return al_photos


# Выводится после выполнения метода
def out_dump():
    try:
        print("\n[99] Назад\n")
        match int(input("Ввод: ").strip()):
            case 99:
                main_menu()
            case _:
                print("Такого варианта нет")
                main_menu()
    except Exception as e:  # Исключения ошибок
        error_log.add('out_dump', e)


# Главное меню
def main_menu():
    try:
        # Получение настроек из файла или его создание если файла нет
        setting.get_dump_config()

        auth_print()

        tprint('Main', 'bulbhead')

        print("[1] Дамп фотографий из всех диалогов")
        print("[2] Дамп фотографий диалога с опр. пользователем")
        print("[3] Дамп фотографий (сохры. и т.д.)")
        print("[4] Дамп фотографий друга(сохры. и т.д)")
        print("[5] Дамп фотографий всех друзей у которых открыты(только сохры)")
        print("\n[111] Настройки")
        print("[0] Выйти из аккаунта")

        setting.check_err()  # Проверяет настройки на ошибки

        match int(input("\nВвод: ").strip()):
            case 1:
                get_dialogs_photo(0)
            case 2:
                get_dialogs_photo(int(input("Введите id пользователя: ").strip()))
            case 3:
                get_photos_friend(0)
            case 4:
                get_photos_friend(int(input("Введите id пользователя: ").strip()))
            case 5:
                get_photos_friends()
            case 111:
                menu_settings()
            case 0:
                clean_exit()
            case _:
                print("Такого варианта нет")
                main_menu()
    except Exception as e:
        error_log.add('main_menu', e)
        main_menu()
    except KeyboardInterrupt:
        sys.exit()


# Меню настроек
def menu_settings(err=""):
    try:
        auth_print()

        tprint('Settings', 'bulbhead')

        if len(err) > 0:
            c_text("red", err)
            err = ""

        print(f'Папка сохранения - {setting.dump_path}')
        # print(f'download(не реализовано) - {download}')
        print(f'dump_to_txt - {dump_txt}')
        print(f'dump_to_html_online - {dump_html}')
        print(f'dump_to_html_offline(Долгий метод) - {dump_html_offline} ')

        if limit_photo == 0:
            print(f'Лимит фотографий - нет')
        else:
            print(f'Лимит фотографий - {limit_photo}')

        if limit_dialog == 0:
            print(f'Лимит диалогов - нет')
        else:
            print(f'Лимит диалогов - {limit_dialog}')

        print("\n[1] Изменить папку сохранения")
        c_text("red", "[2] Изменить download(не реализовано)")
        print("[3] Изменить dump_txt")
        print("[4] Изменить dump_html")
        print("[5] Изменить dump_html offline")
        print("[6] Изменить лимит фотографий")
        print("[7] Изменить лимит диалогов")

        print("\n[90] Сохранить токен в файл")
        print("[91] Удалить сохраненного пользователя")
        print("\n[99] Назад")

        match int(input("\nВвод: ").strip()):
            case 1:
                path_dumps = input("Введите название папки: ").strip()
                setting.set_dump_path(path_dumps)
            # case 2:
            #	if not setting.download:
            #		setting.set_download(True)
            #	else:
            #		setting.set_download(False)
            case 3:
                if not dump_txt:
                    setting.set_dump("dump_txt", True)
                else:
                    setting.set_dump("dump_txt", False)
            case 4:
                if not dump_html:
                    setting.set_dump("dump_html", True)
                else:
                    setting.set_dump("dump_html", False)
            case 5:
                if not dump_html_offline:
                    setting.set_dump("dump_html_offline", True)
                else:
                    setting.set_dump("dump_html_offline", False)

            case 6:
                setting.set_limit_photo(int(input("Введите число: ").strip()))
            case 7:
                setting.set_limit_dialog(int(input("Введите число: ").strip()))
            case 90:
                user = {
                    "name": name,
                    "access_token": login_vk.access_token}
                accessToken.add(user)
                menu_settings()
            case 91:
                user = {
                    "name": name,
                    "access_token": login_vk.access_token}
                accessToken.remove(user)
                menu_settings()
            case 99:
                main_menu()
            case _:
                print("Такого варианта нет")
                menu_settings()
    except Exception as e:
        error_log.add('menu_settings', e)
        menu_settings(str(e))
    except KeyboardInterrupt:
        sys.exit()


# Выход из аккаунта
def clean_exit():
    global login_vk
    login_vk = None

    global login_data
    login_data = {
        "token": "",
        "login": "",
        "password": ""}
    auth_menu()


# Меню авторизации
def auth_menu():
    try:
        # logging.config.fileConfig('logging.conf')

        clear()
        print("Авторизоваться через ")
        print("[-1] Токен")
        print("[-2] Логин и пароль")

        try:
            if exists('auth_vk.json') and accessToken.length() > 0:
                i = 0

                print("\nРанее авторизованные: ")

                for user in accessToken.auth_vks["users"]:
                    print(f"{i} - {user['name']}")
                    i += 1
                i = int(input("\nВыберите способ входа или введите номер: ").strip())

                if i >= 0:
                    login_data['token'] = accessToken.get_token_id(i)
                    collect(False, login_data)
            else:
                inp = int(input("\nВыберите способ входа: ").strip())
        except Exception as e:
            error_log.add("auth_menu accessToken", e)

        clear()

        match inp:
            case -1:
                login_data['token'] = input("Введите токен: ").strip()
                collect(False, login_data)

            # error_log.add('auth_menu', login_data['token'])
            case -2:
                login_data['login'] = str(input("Введите логин: ").strip())
                login_data['password'] = str(input("Введите пароль: ").strip())
                collect(False, login_data)

            # error_log.add('auth_menu', login_data['login'] + " "+ login_data['password']) if debug ==True
            case _:
                print("Такого варианта нет")
                auth_menu()
    except Exception as e:
        error_log.add('auth_menu', e)
    except KeyboardInterrupt:
        sys.exit()


# Выводит кто авторизован
def auth_print():
    try:
        clear()
        print(f'{name} -  Авторизован\n')
    except Exception as e:
        error_log.add('auth_print', e)
    except KeyboardInterrupt:
        sys.exit()


# Устанавливает name, own_id и создает файл photo_pre.html
def get_stand():
    try:
        global name
        global own_id

        name = f'{login_vk.account["first_name"]} {login_vk.account["last_name"]}'
        own_id = login_vk.account["id"]

        with open("photo_pre.html", "w") as file:
            file.write("""<!DOCTYPE HTML>
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                    <title>VK DUMP</title>
                </head>
            <body>
                <div class="full"></div>
                    <div class="body">VK-Dump</div>
                """)

    except Exception as e:  # Исключения ошибок
        error_log.add('get_stand', e)


# Инициализирует вход и чтение настроек
def collect(hide: bool, config: login_data):
    try:
        global login_vk
        login_vk = LoginVK(config)

        global setting
        setting = Settings()

        if login_vk.account["id"] > 0:
            get_stand()
        else:
            raise Exception

        if not hide:
            main_menu()

    except Exception as e:
        error_log.add('collect', e)
    except KeyboardInterrupt:
        sys.exit()


# Цветные сообщения
def c_text(col: str, text):
    try:
        match col:
            case "red":
                color = '\033[31m'
            case "green":
                color = '\033[32m'
            case "blue":
                color = '\033[34m'
            case "yellow":
                color = '\033[33m'
            case "purple":
                color = '\033[35m'
            case "cyan":
                color = '\033[36m'
            case "gray":
                color = '\033[37m'
            case _:
                color = '\033[91m'

        ENDC = '\033[0m'
        print(f'{color}{text}{ENDC}')
    except Exception as e:
        error_log.add('colored', e)
    except KeyboardInterrupt:
        sys.exit()


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content).decode('utf-8')


# Парсер аргументов
def create_parser():
    pars = argparse.ArgumentParser()
    pars.add_argument('-t', '--token', type=str, help='Токен', nargs='?')
    pars.add_argument('-l', '--login', type=str, help='Логин', nargs='?')
    pars.add_argument('-p', '--password', type=str, help='Пароль писать в "" ', nargs='?')
    pars.add_argument('-sp', '--setpath', type=str, help='Название папки для сохранения', nargs='?')
    pars.add_argument('-sd', '--setdumpmethod', type=str, choices=['txt', 'offline', 'online'],
                      help='Метод сохранения данных, offline-фотографии доступны без интернета', nargs='?')
    pars.add_argument('-slp', '--setlimitphoto', type=int, help='Лимит фотографий', nargs='?')
    pars.add_argument('-sld', '--setlimitdialog', type=int, help='Лимит диалогов', nargs='?')
    pars.add_argument('-su', '--saveuser', help='Сохранить пользователя', action='store_true')
    pars.add_argument('-ru', '--removeuser', help='Удалить пользователя', action='store_true')
    pars.add_argument('-m', '--method', type=int,
                      help='1 - Фотографии из всех диалогов\n 2 - Фотографии из опр. диалога \n 3 - Фото из плейлистов \n 4 - Плейлисты опр. пользователя \n 5 - Сохры всех друзей у которых открыты',
                      nargs='+')
    pars.add_argument('-u', '--user', type=int, help='id пользователя для методов 2,4', nargs='?')
    pars.add_argument('-os', '--onlysaved', help='(default:True) в методах 1-5, берётся только альбом с сохрами',
                      action='store_false')
    return pars


# Функции аргументов
def option_parser(argv):
    try:

        if not login_vk:
            if argv.token and not argv.login and not argv.password:
                login_data['token'] = argv.token
                collect(True, login_data)
            elif argv.login and argv.password and not argv.token:
                login_data['login'] = str(argv.login)
                login_data['password'] = str(argv.password)
                collect(True, login_data)
            else:
                raise Exception("Authorization data is not specified, or it is specified incorrectly")

        print("Auth success")

        if argv.setpath or argv.setdumpmethod or argv.setlimitphoto or argv.setlimitdialog or argv.saveuser or argv.removeuser:
            setting.get_dump_config()
            setting.check_err()
            if argv.setpath:
                setting.set_dump_path(argv.setpath, False)
            if argv.setdumpmethod:
                if argv.setdumpmethod == "txt":
                    setting.set_dump_txt(True, bol=False)
                    setting.set_dump_html(False, bol=False)
                    setting.set_dump_html_offline(False, bol=False)
                elif argv.setdumpmethod == "offline":
                    setting.set_dump_txt(False, bol=False)
                    setting.set_dump_html(False, bol=False)
                    setting.set_dump_html_offline(True, bol=False)
                else:
                    setting.set_dump_txt(False, bol=False)
                    setting.set_dump_html(True, bol=False)
                    setting.set_dump_html_offline(False, bol=False)
            if argv.setlimitphoto:
                if argv.setlimitphoto <= 5000:
                    setting.set_limit_photo(argv.setlimitphoto, bol=False)
            if argv.setlimitdialog:
                if argv.setlimitdialog <= 1000:
                    setting.set_limit_photo(argv.setlimitdialog, bol=False)
            if argv.saveuser and not argv.removeuser:
                us = {
                    "name": name,
                    "access_token": login_vk.access_token}
                accessToken.add(us)
            if argv.removeuser and not argv.saveuser:
                us = {
                    "name": name,
                    "access_token": login_vk.access_token}
                accessToken.remove(us)

        if not argv.method:
            raise Exception("Method not specified -m [1;2;3;4;5]")

        if argv.method:
            for m in argv.method:
                match m:
                    case 1:
                        print(f"\n")
                        get_dialogs_photo(0, hide=True)
                    case 2:
                        if argv.user:
                            print(f"\n")
                            get_dialogs_photo(argv.user, hide=True)
                    case 3:
                        print(f"\n")
                        get_photos_friend(0, onlySaved=argv.onlysaved, hide=True)
                    case 4:
                        if argv.user:
                            print(f"\n")
                            get_photos_friend(argv.user, onlySaved=argv.onlysaved, hide=True)
                    case 5:
                        print(f"\n")
                        get_photos_friends(onlySaved=argv.onlysaved, hide=True)
                    case _:
                        raise Exception("Wrong method selected")
    except Exception as err:
        if err.args:
            error_log.add('parameter parser', err.args[0])
        else:
            error_log.add('parameter parser', err)


if __name__ == '__main__':
    try:
        global accessToken
        accessToken = AccessT()

        if len(sys.argv) == 1:
            auth_menu()
        else:
            parser = create_parser()
            option_parser(parser.parse_args(sys.argv[1:]))
        error_log.save_log('error.log')
    except Exception as e:
        error_log.add('colored', e)
    except KeyboardInterrupt:
        sys.exit()
    finally:
        error_log.save_log('error.log')
