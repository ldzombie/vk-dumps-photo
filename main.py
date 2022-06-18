import vk_api
import os
import json
from os import makedirs
from os.path import join, exists
import base64
import requests
import re
import sys

path, filename = os.path.split(os.path.abspath(__file__))


def clear():
    os.system('cls')


debug = False
debug_data = {
    # автоматический вход по токену
    "token": "",
    # id человека для проверки функций
    "user_t_test": 0}

login_data = {
        "token": "",
        "login": "",
        "password": ""}


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
                                          api_version=LoginVK.API_VERSION, auth_handler=self.auth_handler)
                vk_session.auth(token_only=True, reauth=True)

            else:
                raise KeyError('Введите токен или пару логин-пароль')

            self.access_token = vk_session.token['access_token']
            self.vk = vk_session.get_api()
            self.account = self.vk.account.getProfileInfo()
        except Exception as e:
            raise ConnectionError(e)

    @staticmethod
    def auth_handler():
        key = input('Введите код двухфакторой аутентификации: ')
        remember_device = True
        return key, remember_device

    @staticmethod
    def captcha_handler(captcha):
        key = input(f"Введите капчу ({captcha.get_url()}): ").strip()
        return captcha.try_again(key)


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
        try:
            with open('config.json', 'r') as config_file:
                self.def_config = json.load(config_file)
        # auth_menu()
        except Exception as e:
            if "No such file or directory" in str(e):
                self.dump_defconfig()
            # auth_menu()
            error_log.add("Settings __init__", e)

    def dump_defconfig(self):
        try:
            with open('config.json', 'w') as config_file:
                json.dump(self.def_config, config_file)
        except Exception as e:
            error_log.add("Settings dump", e)

    def get_dump_config(self):
        self.limit_photo = self.def_config['setting']['limit_photo']
        self.limit_dialog = self.def_config['setting']['limit_dialog']
        self.dump_path = self.def_config['setting']['path']
        self.download = self.def_config['setting']['download']
        self.dump_txt = self.def_config['setting']['dump_txt']
        self.dump_html = self.def_config['setting']['dump_html']
        self.dump_html_offline = self.def_config['setting']['dump_html_offline']
        self.path_user = f'{path}/{self.dump_path}/{own_id} - {name}'
        makedirs(self.path_user, exist_ok=True)

    def update_settings(self, bol):
        try:

            self.dump_defconfig()
            self.get_dump_config()
            if bol:
                menu_settings()
        except Exception as e:
            error_log.add("update_settings", e)

    def check_err(self):
        if not self.dump_txt and not self.download and not self.dump_html and not self.dump_html_offline:
            self.def_config['setting']['dump_html'] = True
            self.update_settings(False)

    def set_download(self, b):
        self.def_config['setting']['download'] = b
        self.update_settings(True)

    def set_dump_txt(self, b):
        self.def_config['setting']['dump_txt'] = b
        self.update_settings(True)

    def set_dump_html(self, b):
        self.def_config['setting']['dump_html'] = b
        self.update_settings(True)

    def set_dump_html_offline(self, b):
        self.def_config['setting']['dump_html_offline'] = b
        self.update_settings(True)

    def set_limit_photo(self, b):
        self.def_config['setting']['limit_photo'] = b
        self.update_settings(True)

    def set_limit_dialog(self, b):
        self.def_config['setting']['limit_dialog'] = b
        self.update_settings(True)

    def set_dump_path(self, b):
        self.def_config['setting']['path'] = b
        self.update_settings(True)


class AccessT:
    auth_vks = {"users": []}

    def __init__(self):
        try:
            with open('auth_vk.json', 'r') as file:
                self.auth_vks = json.load(file)
        except Exception as e:
            if "No such file or directory" in str(e):
                self.dump()
            error_log.add("AccessT __init__", e)

    def dump(self):
        try:
            with open('auth_vk.json', 'w') as file:
                json.dump(self.auth_vks, file)
        except Exception as e:
            error_log.add("Access dump", e)

    def add(self, user):
        self.auth_vks["users"].append(user)
        self.dump()

    def get_token_id(self, index):
        return self.auth_vks["users"][int(index)]["access_token"]

    def length(self):
        return len(self.auth_vks["users"])


# Фотографии из диалогов и из диалога если указать id
def get_dialogs_photo(p_id):
    try:
        update_variables()

        if dump_html or dump_html_offline:
            file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
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
                    # Нужно чтобы получить все фотографии из диалога, если их больше 200
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
        print(f"Начинаю выгрузку фотографий | {name} - vk.com/id{p_id}")

        path_dialog = f'{path_user}/dialog'

        makedirs(f'{path_dialog}', exist_ok=True)

        for dialog in all_dialogs:  # Идем по списку
            if p_id > 0:
                idd = dialog["peer"]["id"]
                peer_type = dialog['peer']['type']  # Информация о диалоге
            else:
                idd = dialog["conversation"]["peer"]["id"]  # Вытаскиваем ID человека с  диалога
                peer_type = dialog['conversation']['peer']['type']  # Информация о диалоге (конференция это или человек)

            if peer_type == "user":  # Ставим проверку конференции
                if idd > 0:  # Ставим проверку на группы
                    print(f"Выгрузка фотографий - {idd}")
                    b = login_vk.vk.users.get(user_ids=idd)[0]  # Получаем информацию о человеке

                    fio = f'{b["first_name"]} {b["last_name"]}'

                    if limit_photo == 0 or limit_photo > 200:

                        fo = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo', start_from=0,
                                                                        count=200,
                                                                        preserve_order=1, max_forwards_level=45)
                        a_photo = fo["items"]

                        if len(a_photo) == 200:
                            offset = fo["next_from"]  # сдвиг начала отсчёта
                            while True:
                                if limit_photo != 0:
                                    count = limit_photo - len(a_photo)
                                    if count > 200:
                                        count = 200
                                    if count == 0 or count < 0:
                                        break
                                else:
                                    count = 200
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
                                # Проверка на то нужно ли делать ещё один цикл, и не превышает ли фисло фотографий лимит
                                if length == 200 and length_all < limit_photo or length == 200 and limit_photo == 0:
                                    offset = fo1["next_from"]
                                else:
                                    break
                    else:
                        fo = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo', start_from=0,
                                                                        count=limit_photo,
                                                                        preserve_order=1, max_forwards_level=45)
                        a_photo = fo["items"]

                    if len(a_photo) == 0:
                        break

                    for i in a_photo:  # Идем по списку вложений
                        for j in i["attachment"]["photo"]["sizes"]:
                            if 500 < j["height"] < 650:  # Проверка размеров
                                url = j["url"]  # Получаем ссылку на изображение
                                if dump_txt:
                                    urls.append(url)
                                if dump_html and not dump_html_offline:
                                    file += f'<img class="photos" src="{url}" alt="Не удалось загрузить (:" ' \
                                            f'title="Найдено в диалоге - vk.com/id{idd}">'  # Сохраняем в переменную
                                if dump_html_offline:
                                    base = get_as_base64(url)
                                    file += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось ' \
                                            f'загрузить (:" title="Найдено в альбоме - {idd}"> '
                                break
                    if dump_html or dump_html_offline:

                        try:
                            save_photo = open(f'{path_dialog}/{idd} - {fio}.html', 'w+',
                                              encoding="utf8")  # Открываем файл
                        except Exception:
                            save_photo = open(f'{path_dialog}/Не определенно.html', 'w+', encoding="utf8")
                        save_photo.write(file)  # Сохраняем диалог
                        save_photo.close()  # Закрываем
                        file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
                    if dump_txt:
                        dialogs.append({'name': '_'.join(fio), 'photos': urls})
                        urls = []
                    print(f"Выгруженно {len(a_photo)} фотографий")
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

        print("Выгрузка фотографий из диалогов завершена")
        out_dump()
    except Exception as e:  # Исключения ошибок
        error_log.add('get_dialogs_photo', e)
        print(e)
        out_dump()
    except KeyboardInterrupt:
        out_dump()


# Фотографии из плейлистов
def get_photos_profile():
    try:
        update_variables()

        path_albums = f'{path_user}/albums'
        if dump_txt:
            json_albums = []
            urls = []
        if dump_html or dump_html_offline:
            file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
        albums = login_vk.vk.photos.getAlbums(need_system=1)
        num = albums["count"]  # Количество альбомов
        print(f"Всего найдено альбомов: {num}")
        print(f"Начинаю выгрузку фотографий")

        makedirs(f'{path_user}/albums', exist_ok=True)

        for album in albums["items"]:
            idd = album["id"]
            title = album["title"]
            size = album["size"]
            if size == 0:
                continue

            print(f"{title} - Фото: {size}")
            if limit_photo == 0 or limit_photo > 1000:

                a_photos = login_vk.vk.photos.get(album_id=idd, photo_sizes=1, rev=1, count=200, offset=0)["items"]
                if len(a_photos) == 1000:
                    offset = 1000  # сдвиг начала отсчёта
                    while True:  # получаем все фотографии если их больше 1000
                        if limit_photo != 0:
                            count = limit_photo - len(a_photos)
                            if count > 1000:
                                count = 1000
                            if count == 0 or count < 0:
                                break
                        else:
                            count = 1000
                        fo1 = login_vk.vk.photos.get(album_id=idd, photo_sizes=1, rev=1, count=count, offset=offset)[
                            "items"]

                        length = len(fo1["items"])
                        if length > 0:
                            a_photos += fo1["items"]
                        else:
                            break

                        if length == 1000 and len(a_photos) < limit_photo or limit_photo == 0 and length == 1000:
                            offset += 1000
                        else:
                            break

            else:
                a_photos = login_vk.vk.photos.get(album_id=idd, photo_sizes=1, rev=1, count=limit_photo, offset=0)[
                    "items"]

            for i in a_photos:  # Идем по списку вложений
                for j in i["sizes"]:
                    if 500 < j["height"] < 650:  # Проверка размеров
                        url = j["url"]  # Получаем ссылку на изображение
                        if dump_txt:
                            urls.append(url)
                        if dump_html and not dump_html_offline:
                            file += f'<img class="photos" src="{url}" alt="Не удалось загрузить (:" title="Найдено в ' \
                                    f'альбоме - {idd}">'  # Сохраняем в переменную
                        if dump_html_offline:
                            base = get_as_base64(url)
                            file += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось ' \
                                    f'загрузить (:" title="Найдено в альбоме - {idd}"> '
                        break  # чтобы не добавляло одинаковых фото
            if dump_txt:
                json_albums.append({'name': "_".join(title.split(' ')), 'photos': urls})

            print(f"Выгруженно {len(a_photos)} фотографий")
            if dump_html or dump_html_offline:
                save_photo = open(f'{path_albums}/{title}.html', 'w+', encoding="utf8")  # Открываем файл
                save_photo.write(file)  # Сохраняем диалог
                save_photo.close()  # Закрываем
                file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
        if dump_txt:
            with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                json.dump(json_albums, alb_file)

        print("Выгрузка фотографий из альбомов завершена")
        out_dump()
    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_profile', e)
        print(e)
        out_dump()
    except KeyboardInterrupt:
        out_dump()


# Фотографии из плейлистов пользователя
def get_photos_friend(user_id):
    try:
        update_variables()

        user = login_vk.vk.users.get(user_ids=user_id)[0]
        fio = f'{user["first_name"]} {user["last_name"]}'

        if dump_html or dump_html_offline:
            file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()
        if dump_txt:
            json_albums = []
            urls = []
        albums = login_vk.vk.photos.getAlbums(owner_id=user_id, need_system=1)

        num = albums["count"]  # Количество альбомов
        print(f"Всего найдено альбомов: {num}")
        print(f"Начинаю выгрузку фотографий")

        path_user_friend = f'{path}/dump/{user_id} - {fio}'
        path_albums = f'{path_user_friend}/albums'

        makedirs(f'{path_user_friend}/albums', exist_ok=True)

        for album in albums["items"]:
            idd = album["id"]
            title = album["title"]
            count = album["size"]
            if count == 0:
                continue
            print(f"{title} - Фото: {count}")

            a_photos = \
                login_vk.vk.photos.get(owner_id=user_id, album_id=idd, photo_sizes=1, rev=1, count=1000, offset=0)[
                    "items"]
            if count > 1000 and len(a_photos) < limit_photo or count > 1000 and limit_photo == 0:
                offset = 1000  # сдвиг начала отсчёта
                while True:  # получаем все фотографии если их больше 1000
                    a_photos += login_vk.vk.photos.get(owner_id=user_id, album_id=idd, photo_sizes=1, rev=1, count=1000,
                                                       offset=offset)["items"]

                    if len(a_photos) >= limit_photo or count == len(a_photos):
                        break
                    else:
                        offset += 1000

            for i in a_photos:  # Идем по списку вложений
                for j in i["sizes"]:
                    if 500 < j["height"] < 650:  # Проверка размеров
                        url = j["url"]  # Получаем ссылку на изображение
                        if dump_txt:
                            urls.append(url)
                        if dump_html and not dump_html_offline:
                            file += f'<img class="photos" src="{url}" alt="Не удалось загрузить (:" title="Найдено в альбоме - {idd}">'  # Сохраняем в переменную
                        if dump_html_offline:
                            base = get_as_base64(url)
                            file += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось загрузить (:" title="Найдено в альбоме - {idd}">'
                        break  # чтобы не добавляло одинаковых фото
            if dump_txt:
                json_albums.append({'name': "_".join(title.split(' ')), 'photos': urls})

            print(f"Выгруженно {len(a_photos)} фотографий")
            if dump_html or dump_html_offline:
                save_photo = open(f'{path_albums}/{title}.html', 'w+', encoding="utf8")  # Открываем файл
                save_photo.write(file)  # Сохраняем диалог
                save_photo.close()  # Закрываем
        if dump_txt:
            with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                json.dump(json_albums, alb_file)
        print("Выгрузка фотографий из альбомов завершена")
        out_dump()
    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friend', e)
        print(e)
        out_dump()
    except KeyboardInterrupt:
        out_dump()


# Фотографии из плейлистов друзей с открытыми сохрами
def get_photos_friends():
    try:
        update_variables()
        if debug:
            deb_count = 0
        friends = login_vk.vk.friends.get(fields="1", order="hints", name_case="nom", count=250)
        print("Общее количество пользователей: " + str(friends['count']))
        for friend in friends['items']:
            friend_id = friend['id']

            if debug:
                print(deb_count)
                deb_count += 1

            try:
                albums = login_vk.vk.photos.getAlbums(owner_id=friend_id, album_ids="-15")
                if albums['count'] == 0 or not albums['items'][0]['id'] == -15:
                    continue
            except Exception:
                continue

            if dump_txt:
                json_albums = []
                urls = []
            if dump_html or dump_html_offline:
                file = open(f'{path}/photo_pre.html', 'r', encoding="utf8").read()

            fio = f'{friend["first_name"]} {friend["last_name"]}'

            print(f"Начинаю выгрузку фотографий " + fio)
            path_user_friend = f'{path}/dump/{friend_id} - {fio}'
            path_albums = f'{path_user_friend}/albums'
            makedirs(f'{path_user_friend}/albums', exist_ok=True)

            idd = albums['items'][0]['id']
            title = albums['items'][0]["title"]
            count = albums['items'][0]["size"]
            print(f"{title} - Фото: {count}")
            a_photos = \
                login_vk.vk.photos.get(owner_id=friend_id, album_id=idd, photo_sizes=1, rev=1, count=1000, offset=0)[
                    "items"]
            if count > 1000 and len(a_photos) < limit_photo or count > 1000 and limit_photo == 0:
                offset = 1000  # сдвиг начала отсчёта
                while True:  # получаем все фотографии если их больше 1000
                    a_photos += \
                        login_vk.vk.photos.get(owner_id=friend_id, album_id=idd, photo_sizes=1, rev=1, count=1000,
                                               offset=offset)["items"]

                    if len(a_photos) >= limit_photo or count == len(a_photos):
                        break
                    else:
                        offset += 1000

            for i in a_photos:  # Идем по списку вложений
                for j in i["sizes"]:
                    if 500 < j["height"] < 650:  # Проверка размеров
                        url = j["url"]  # Получаем ссылку на изображение
                        if dump_txt:
                            urls.append(url)
                        if dump_html and not dump_html_offline:
                            file += f'<img class="photos" src="{url}" alt="Не удалось загрузить (:" title="Найдено в альбоме - {idd}">'  # Сохраняем в переменную
                        if dump_html_offline:
                            base = get_as_base64(url)
                            file += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось загрузить (:" title="Найдено в альбоме - {idd}">'
                        break  # чтобы не добавляло одинаковых фото
            if dump_txt:
                json_albums.append({'name': "_".join(title.split(' ')), 'photos': urls})
            print(f"Выгруженно {len(a_photos)} фотографий")
            if dump_html or dump_html_offline:
                save_photo = open(f'{path_albums}/{title}.html', 'w+', encoding="utf8")  # Открываем файл
                save_photo.write(file)  # Сохраняем диалог
                save_photo.close()  # Закрываем
            if dump_txt:
                with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                    json.dump(json_albums, alb_file)
        print("Выгрузка фотографий из альбома завершена")
        out_dump()

    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friends', e)
        print(e)
        out_dump()
    except KeyboardInterrupt:
        out_dump()


# переменные
def update_variables():
    try:
        global limit_dialog
        global limit_photo
        global dump_txt
        global dump_html
        global dump_html_offline
        global path_user

        limit_dialog = setting.limit_dialog
        limit_photo = setting.limit_photo
        dump_txt = setting.dump_txt
        dump_html = setting.dump_html
        dump_html_offline = setting.dump_html_offline
        path_user = setting.path_user

    except Exception as e:  # Исключения ошибок
        error_log.add('update_variables', e)
        print(e)
    except KeyboardInterrupt:
        sys.exit()


def out_dump():
    try:
        print(" ")
        print("[99] Назад")
        print(" ")
        inp = int(input("Ввод: "))
        match inp:
            case 99:
                main_menu()
            case _:
                print("Такого варианта нет")
                main_menu()
    except Exception as e:  # Исключения ошибок
        error_log.add('out_dump', e)


def main_menu():
    try:
        setting.get_dump_config()
        auth_print()

        print("[1] Дамп фотографий из всех диалогов")
        print("[2] Дамп фотографий диалога с опр. пользователем")
        print("[3] Дамп фотографий (сохры. и т.д.)")
        print("[4] Дамп фотографий друга(сохры. и т.д)")
        print("[5] Дамп фотографий всех друзей у которых открыты(только сохры)")
        print(" ")
        print("[111] Настройки")
        print("[0] Выйти из аккаунта")
        print(" ")

        setting.check_err()

        inp = int(input("Ввод: "))
        match inp:
            case 1:
                get_dialogs_photo(0)
            case 2:
                i = int(input("Введите id пользователя: ")) if not debug or (
                        debug and debug_data["user_t_test"] == 0) else debug_data["user_t_test"]
                get_dialogs_photo(i)
            case 3:
                get_photos_profile()
            case 4:
                i = int(input("Введите id пользователя: ")) if not debug or (
                        debug and debug_data["user_t_test"] == 0) else debug_data["user_t_test"]
                get_photos_friend(i)
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


def menu_settings(err=""):
    try:
        auth_print()

        if len(err) > 0:
            c_text("red", err)

        print(f'Папка сохранения - {setting.dump_path}')
        print(f'download - {setting.download}')
        print(f'dump_to_txt - {setting.dump_txt}')
        print(f'dump_to_html_online - {setting.dump_html}')
        print(f'dump_to_html_offline(Долгий метод) - {setting.dump_html_offline} ')

        if setting.limit_photo == 0:
            print(f'Лимит фотографий - нет')
        else:
            print(f'Лимит фотографий - {setting.limit_photo}')

        if setting.limit_dialog == 0:
            print(f'Лимит диалогов - нет')
        else:
            print(f'Лимит диалогов - {setting.limit_dialog}')

        print(" ")

        print("[1] Изменить папку сохранения")
        print("[2] Изменить download(не реализовано)")
        print("[3] Изменить dump_txt")
        print("[4] Изменить dump_html")
        print("[5] Изменить dump_html offline")
        print("[6] Изменить лимит фотографий")
        print("[7] Изменить лимит диалогов")

        print(" ")
        print("[90] Сохранить токен в файл")
        print("[99] Назад")
        print(" ")

        inp = int(input("Ввод: "))
        match inp:
            case 1:
                path_dumps = input("Введите название папки: ")
                setting.set_dump_path(path_dumps)
            # case 2:
            #	if not setting.download:
            #		setting.set_download(True)
            #	else:
            #		setting.set_download(False)
            case 3:
                if not setting.dump_txt:
                    setting.set_dump_txt(True)
                else:
                    setting.set_dump_txt(False)
            case 4:
                if not setting.dump_html:
                    setting.set_dump_html(True)
                else:
                    setting.set_dump_html(False)
            case 5:
                if not setting.dump_html_offline:
                    setting.set_dump_html_offline(True)
                else:
                    setting.set_dump_html_offline(False)

            case 6:
                lim = int(input("Введите число: "))
                setting.set_limit_photo(lim)
            case 7:
                lim = int(input("Введите число: "))
                setting.set_limit_dialog(lim)
            case 90:
                user = {
                    "name": name,
                    "access_token": login_vk.access_token}
                accessToken.add(user)
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


def clean_exit():
    global login_vk
    login_vk = None

    global login_data
    login_data = {
        "token": "",
        "login": "",
        "password": ""}
    auth_menu()


def auth_menu():
    global accessToken
    accessToken = AccessT()
    try:
        # logging.config.fileConfig('logging.conf')

        clear()
        print("Авторизоваться через ")
        print("[1] Токен")
        print("[2] Логин и пароль")

        inp = int(input("Выберите способ входа: ")) if not debug else 1

        match inp:
            case 1:
                try:
                    if debug:
                        raise Exception

                    if not exists('auth_vk.json'):
                        raise Exception

                    if accessToken.length() > 0:
                        i = 0
                        print("Ранее авторизованные: ")

                        for user in accessToken.auth_vks["users"]:
                            print(f"{i} - {user['name']}")
                            i += 1
                        inp = input("Введите токен или номер: ")
                        regex = "^[a-zA-Z]+$"
                        pattern = re.compile(regex)

                        if pattern.search(inp) is None:
                            login_data['token'] = accessToken.get_token_id(inp)
                        else:
                            login_data['token'] = str(inp)
                    else:
                        raise Exception
                except Exception as e:
                    print(e)
                    login_data['token'] = input("Введите токен: ") if not debug else debug_data['token']

                collect(login_data)

            # error_log.add('auth_menu', login_data['token'])
            case 2:
                login_data['login'] = str(input("Введите логин: "))
                login_data['password'] = str(input("Введите пароль: "))
                collect(login_data)

            # error_log.add('auth_menu', login_data['login'] + " "+ login_data['password']) if debug ==True
            case _:
                print("Такого варианта нет")
                auth_menu()
    except Exception as e:
        error_log.add('auth_menu', e)
    except KeyboardInterrupt:
        sys.exit()


def auth_print():
    try:
        clear()
        print(f'{name} -  Авторизован')
        print(" ")
    except Exception as e:
        error_log.add('auth_print', e)
    except KeyboardInterrupt:
        sys.exit()


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
                    <div class="body">VK-DUMP</div>
                """)

    except Exception as e:  # Исключения ошибок
        error_log.add('get_stand', e)


def collect(config):
    try:
        global login_vk
        login_vk = LoginVK(config)

        global setting
        setting = Settings()

        if login_vk.account["id"] > 0:
            get_stand()
            main_menu()

    except Exception as e:
        error_log.add('collect', e)
    except KeyboardInterrupt:
        sys.exit()


def c_text(col, text):
    try:
        match col:
            case "red":
                color = '\033[91m'
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


if __name__ == '__main__':
    try:
        auth_menu()
        error_log.save_log('error.log')
    except Exception as e:
        error_log.add('colored', e)
    except KeyboardInterrupt:
        sys.exit()
    finally:
        error_log.save_log('error.log')
