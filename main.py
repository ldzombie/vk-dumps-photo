import argparse
import json
from os import makedirs
from os.path import join, exists

from art import tprint

from modules.c_access_token import AccessT
from modules.c_auth import LoginVK, clean_login_data, login_data, set_path_user
from modules.c_error import ErrorLog
from modules.c_settings import Settings
from modules.oth_function import *

# globals
json_albums = []

error_log = ErrorLog()


# Фотографии из диалогов
def get_dialogs_photo(users_ids: list = None):
    try:
        if setting.dump_html or setting.dump_html_offline:
            imgs = ""
        if setting.dump_txt:
            urls = []
            dialogs = []
        if users_ids is not None:
            all_dialogs = []
            for i in range(len(users_ids)):
                test = login_vk.vk.messages.getConversationsById(peer_ids=users_ids[i])
                all_dialogs += test["items"]
        else:
            if setting.limit_dialog == 0 or setting.limit_dialog > 200:
                test = login_vk.vk.messages.getConversations(count=200)  # Получаем диалоги через токен
                all_dialogs = test["items"]

                if len(all_dialogs) == 200:
                    # Нужно, чтобы получить все диалоги, если их больше 200
                    offset = 200  # сдвиг начала отсчёта
                    while True:
                        setting.intervals()
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
                all_dialogs = login_vk.vk.messages.getConversations(count=setting.limit_dialog)["items"]

        num = len(all_dialogs)
        # Количество диалогов
        print(f"Всего найдено диалогов: {num}")
        print(f"Начинаю выгрузку фотографий | {login_vk.name} - vk.com/id{login_vk.own_id}")

        path_dialog = f'{path_user}/dialog'

        for dialog in all_dialogs:  # Идем по списку
            if users_ids is not None:
                idd = dialog["peer"]["id"]
                peer_type = dialog['peer']['type']  # Информация о диалоге
            else:
                idd = dialog["conversation"]["peer"]["id"]  # Вытаскиваем ID человека с диалога
                peer_type = dialog['conversation']['peer']['type']  # Информация о диалоге (конференция это или человек)

            if peer_type == "user":  # Ставим проверку конференции
                if idd > 0:  # Ставим проверку на группы

                    b = login_vk.vk.users.get(user_ids=idd)[0]  # Получаем информацию о человеке

                    fio = f'{b["first_name"]} {b["last_name"]}'

                    print(f"Выгрузка фотографий - {idd} - {fio}")

                    if setting.limit_photo <= 200 and not setting.limit_photo == 0:
                        setting.intervals()
                        fo = login_vk.vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo', start_from=0,
                                                                        count=setting.limit_photo,
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
                                if setting.limit_photo == 0:
                                    count = 200
                                else:
                                    count = setting.limit_photo - len(a_photo)
                                    if count >= 200:
                                        count = 200
                                    if count == 0 or count < 0:
                                        break
                                setting.intervals()
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
                                if length == 200 and length_all < setting.limit_photo or length == 200 and setting.limit_photo == 0:
                                    offset = fo1["next_from"]
                                else:
                                    break

                    if len(a_photo) == 0:
                        continue

                    for i in a_photo:  # Идем по списку вложений
                        for j in i["attachment"]["photo"]["sizes"]:
                            if setting.check_sizes(j["height"]) or setting.check_sizes(j["width"]):  # Проверка размеров
                                url = j["url"]  # Получаем ссылку на изображение
                                if setting.dump_txt:
                                    urls.append(url)
                                if setting.dump_html and not setting.dump_html_offline:
                                    imgs += f'<img class="photos" src="{url}" alt="Не удалось загрузить" ' \
                                            f'title="Найдено в диалоге - vk.com/id{idd}">'  # Сохраняем в переменную
                                if setting.dump_html_offline:
                                    base = get_as_base64(url)
                                    imgs += f'<img class="photos" src="data:image/png;base64,{base}" ' \
                                            f'alt="Не удалось загрузить " title="Найдено в альбоме - {idd}">'
                                break  # чтобы не сохраняло одинаковые фотографии разного размера
                    if setting.dump_html or setting.dump_html_offline:
                        try:
                            makedirs(f'{path_dialog}', exist_ok=True)
                            with (open(f'{path_dialog}/{idd} - {fio}.html', 'w+', encoding="utf8") as save_photo,
                                  open(f'{path}/photo_pre.html', 'r', encoding="utf8") as photo_pre):
                                save_photo.write(photo_pre.read() + imgs)
                        except Exception as e:
                            error_log.add("get_dialogs_photo save_photo", e)

                        imgs = ""
                    if setting.dump_txt:
                        dialogs.append({'name': '_'.join(fio), 'photos': urls})
                        urls = []
                    c_text(Color.GREEN, f"[+]Выгруженно {len(a_photo)} фотографий")
                else:
                    print("Это группа!")
            else:
                print("Это конфа!")

        if setting.dump_txt:
            file_name = 'dialogs.json'

            with open(join(f'{path_dialog}', file_name), 'w') as alb_file:
                json.dump(dialogs, alb_file)

        c_text(Color.PURPLE, "\nВыгрузка фотографий из диалогов завершена")
        if not setting.show_off:
            out_dump()
    except Exception as e:  # Исключения ошибок
        error_log.add('get_dialogs_photo', e)
        print(e)
        if not setting.show_off:
            out_dump()


# Фотографии из плейлистов пользователя по id
def get_photos_friend(user_id: int):
    try:
        global json_albums

        if user_id == 0:
            user_id = login_vk.own_id
            path_albums = f'{path_user}/albums'
        else:
            user = login_vk.vk.users.get(user_ids=user_id)[0]
            fio = f'{user["first_name"]} {user["last_name"]}'
            path_user_friend = f'{path}/dump/{user_id} - {fio}'
            path_albums = f'{path_user_friend}/albums'

        if setting.album_only_saved:
            albums = login_vk.vk.photos.getAlbums(owner_id=user_id, album_ids="-15")
        else:
            albums = login_vk.vk.photos.getAlbums(owner_id=user_id, need_system=1)

        num = albums["count"]  # Количество альбомов

        print(f"Всего найдено альбомов: {num}")

        if num == 0:
            raise Exception

        print(f"Начинаю выгрузку фотографий")

        for album in albums["items"]:
            idd = album["id"]
            title = album["title"]
            size = album["size"]
            if size == 0:
                continue

            print(f"{title} - Фото: {size}")

            a_photos = get_album_photo(user_id, idd, size, path_albums, title)

            c_text(Color.GREEN, f"[+]Выгруженно {a_photos} фотографий")

        if setting.dump_txt:
            with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                json.dump(json_albums, alb_file)
            json_albums=[]
        c_text(Color.PURPLE, "\nВыгрузка фотографий из альбомов завершена")
        if not setting.show_off:
            out_dump()
    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friend', e)
        print(c_text(Color.RED, e))
        if not setting.show_off:
            out_dump()


# Фотографии из плейлистов друзей с открытыми сохрами
def get_photos_friends():
    global json_albums
    try:
        friends = login_vk.vk.friends.get(fields="1", order="hints", name_case="nom", count=250)
        print("Общее количество пользователей: " + str(friends['count']))
        for friend in friends['items']:
            friend_id = friend['id']
            try:
                if setting.album_only_saved:
                    albums = login_vk.vk.photos.getAlbums(owner_id=friend_id, album_ids="-15")
                else:
                    albums = login_vk.vk.photos.getAlbums(owner_id=friend_id, album_ids="-15", need_system=1)

                if albums['count'] == 0:
                    continue
            except Exception as e:
                print(c_text(Color.RED, e))
                continue

            friend_fio = f'{friend["first_name"]} {friend["last_name"]}'
            path_user_friend = f'{path}/dump/{friend_id} - {friend_fio}'
            path_albums = f'{path_user_friend}/albums'

            idd = albums['items'][0]['id']
            title = albums['items'][0]["title"]
            size = albums['items'][0]["size"]

            # если файл с этим альбомом же существует, то альбом пропускается
            if exists(f"{path_albums}/{title}-0.html"):
                print(f"{friend_fio} - Skip")
                continue

            print(f"Начинаю выгрузку фотографий " + friend_fio)

            print(f"{title} - Фото: {size}")

            a_photos = get_album_photo(friend_id, idd, size, path_albums, title)

            c_text(Color.GREEN, f"[+]Выгруженно {a_photos} фотографий")

            if setting.dump_txt:
                with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                    json.dump(json_albums, alb_file)
                json_albums = []
        c_text(Color.PURPLE, "\nВыгрузка фотографий из альбома завершена")
        if not setting.show_off:
            out_dump()

    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friends', e)
        print(e)
        if not setting.show_off:
            out_dump()


# Метод для получения всех фотографий из альбома
def get_album_photo(user_id: int, album_id: int, siz: int, path_albums: str, title: str) -> int:
    try:
        cc, num, al_size = 1, 0, 0

        if setting.limit_photo == 0 or setting.limit_photo > 1000:
            al_photos = login_vk.vk.photos.get(owner_id=user_id,
                                               album_id=album_id,
                                               photo_sizes=1,
                                               rev=1,
                                               count=1000,
                                               offset=0)["items"]
            al_size += len(al_photos)

            if len(al_photos) == 1000:
                offset = 1000
                while True:  # получаем все фотографии если их больше 1000
                    # сдвиг начала отсчёта
                    if setting.limit_photo == 0:
                        count = siz - len(al_photos)
                    else:
                        count = setting.limit_photo - len(al_photos)
                        if count <= 0:
                            break

                    if count > 1000:
                        count = 1000
                    if count <= 0:
                        break

                    setting.intervals()
                    fo1 = login_vk.vk.photos.get(owner_id=user_id,
                                                 album_id=album_id,
                                                 photo_sizes=1,
                                                 rev=1,
                                                 count=count,
                                                 offset=offset)["items"]
                    length = len(fo1)
                    if length > 0:
                        al_photos += fo1
                        al_size += length
                        cc += 1
                    else:
                        break

                    if cc % setting.s_rod == 0:
                        save_file_html(al_photos, album_id, path_albums, f'{title}-{num}')
                        num += 1
                        siz -= len(al_photos)
                        al_photos = []

                    if siz > len(al_photos) and (len(al_photos) < setting.limit_photo or setting.limit_photo == 0):
                        offset = al_size
                    else:
                        break

            if len(al_photos) > 0:
                save_file_html(al_photos, album_id, path_albums, f'{title}-{num}')
        else:
            al_photos = login_vk.vk.photos.get(owner_id=user_id,
                                               album_id=album_id,
                                               photo_sizes=1,
                                               rev=1,
                                               count=setting.limit_photo)["items"]
            al_size += len(al_photos)
            save_file_html(al_photos, album_id, path_albums, f'{title}-0')
        return al_size
    except Exception as e:
        error_log.add("get_album_photo", e)


# Проходит по всем фотографиям и находит подходящий размер фото, после сохраняет в файл
def save_file_html(photos: list, idd: str, path_albums: str, title: str):
    try:
        global json_albums

        l_urls = []
        l_imgs = ""

        for i in photos:  # Идем по списку вложений
            for j in i["sizes"]:
                if setting.check_sizes(j["height"]) or setting.check_sizes(j["width"]):  # Проверка размеров
                    url = j["url"]  # Получаем ссылку на изображение
                    if setting.dump_txt:
                        l_urls.append(url)
                    if setting.dump_html and not setting.dump_html_offline:
                        l_imgs += f'<img class="photos" src="{url}" alt="Не удалось загрузить" ' \
                                  f'title="Найдено в альбоме - {idd}">'  # Сохраняем в переменную
                    if setting.dump_html_offline:
                        base = get_as_base64(url)
                        l_imgs += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось загрузить" ' \
                                  f'title="Найдено в альбоме - {idd}">'
                    break  # чтобы не добавляло одинаковых фото

        if setting.dump_html or setting.dump_html_offline:
            try:
                makedirs(f'{path_albums}', exist_ok=True)
                with (open(f'{path_albums}/{title}.html', 'w+', encoding="utf8") as save_photo,
                      open(f'{path}/photo_pre.html', 'r', encoding="utf8") as photo_pre):
                    save_photo.write(photo_pre.read() + l_imgs)

            except Exception as e:
                error_log.add("save_file_html", e)
        if setting.dump_txt:
            json_albums.append({'name': "_".join(title.split(' ')), 'photos': l_urls})
            print(len(l_urls))
    except Exception as e:
        error_log.add("save_file", e)


# Выводится после выполнения метода
def out_dump():
    try:
        print("\n[99] Назад\n")
        match int(input("Ввод: ").strip()):
            case 99:
                menu_main()
            case _:
                print("Такого варианта нет")
                menu_main()
    except Exception as e:  # Исключения ошибок
        error_log.add('out_dump', e)


# Главное меню
def menu_main():
    try:
        clear()
        # Получение настроек из файла или его создание если файла нет
        setting.get_dump_config()

        login_vk.auth_print()

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
                get_dialogs_photo()
            case 2:
                get_dialogs_photo(list(map(int, input("Введите id пользователя: ").strip().split())))
            case 3:
                get_photos_friend(0)
            case 4:
                z = list(map(int, input("Введите id пользователя: ").strip().split()))
                for i in z:
                    get_photos_friend(i)
            case 5:
                get_photos_friends()
            case 111:
                menu_settings()
            case 0:
                clean_exit()
            case _:
                print("Такого варианта нет")
                menu_main()
    except Exception as e:
        error_log.add('main_menu', e)
        menu_main()
    except KeyboardInterrupt:
        sys.exit()


# Меню настроек
def menu_settings(err=""):
    try:
        clear()
        login_vk.auth_print()

        tprint('Settings', 'bulbhead')

        if len(err) > 0:
            c_text(Color.RED, err)
            err = ""

        print(f'Папка сохранения - {setting.dump_path}')
        print(f'dump_to_txt - {setting.dump_txt}')
        print(f'dump_to_html_online - {setting.dump_html}')
        print(f'dump_to_html_offline(Долгий метод) - {setting.dump_html_offline} ')
        print(f'interval - {setting.a_interval}')
        if setting.a_interval:
            print(f'interval_value - {setting.interval_values}')

        if setting.limit_photo == 0:
            print(f'Лимит фотографий - нет')
        else:
            print(f'Лимит фотографий - {setting.limit_photo}')

        if setting.limit_dialog == 0:
            print(f'Лимит диалогов - нет')
        else:
            print(f'Лимит диалогов - {setting.limit_dialog}')

        print("\n[1] Изменить папку сохранения")
        print("[2] Изменить dump_txt")
        print("[3] Изменить dump_html")
        print("[4] Изменить dump_html offline")
        print("[5] Изменить interval")
        if setting.a_interval:
            print("[6] Изменить значения интервала")
        print("[7] Изменить лимит фотографий")
        print("[8] Изменить лимит диалогов")

        print("\n[90] Сохранить токен в файл")
        print("[91] Удалить сохраненного пользователя")
        print("\n[99] Назад")

        match int(input("\nВвод: ").strip()):
            case 1:
                path_dumps = input("Введите название папки: ").strip()
                setting.set_dump_path(path_dumps)
            case 2:
                setting.set_dump("dump_txt", not setting.dump_txt)
            case 3:
                setting.set_dump("dump_html", not setting.dump_html)
            case 4:
                setting.set_dump("dump_html_offline", not setting.dump_html_offline)
            case 5:
                setting.set_dump("a_interval", not setting.a_interval)
            case 6:
                x = input("Введите 2 числа: ").strip().split()
                setting.set_interval_values(list(map(int, x)))
            case 7:
                setting.set_limit_photo(int(input("Введите число: ").strip()))
            case 8:
                setting.set_limit_dialog(int(input("Введите число: ").strip()))
            case 90:
                user = {
                    "name": login_vk.name,
                    "access_token": login_vk.access_token}
                accessToken.add(user)
            case 91:
                user = {
                    "name": login_vk.name,
                    "access_token": login_vk.access_token}
                accessToken.remove(user)
            case 99:
                menu_main()
            case _:
                print("Такого варианта нет")

        menu_settings()
    except Exception as e:
        error_log.add('menu_settings', e)
        menu_settings(str(e))
    except KeyboardInterrupt:
        sys.exit()


# Меню авторизации
def menu_auth():
    try:
        clear()
        print("Авторизоваться через ")
        print("[-1] Токен")
        print("[-2] Логин и пароль")

        if accessToken.length() > 0:

            accessToken.get_users()

            inp = int(input("\nВыберите способ входа или введите номер: ").strip())

            if inp >= 0:
                login_data['token'] = accessToken.get_token_id(inp)
                collect(login_data)
        else:
            inp = int(input("\nВыберите способ входа: ").strip())
            if inp < 0:
                match inp:
                    case -1:
                        login_data['token'] = input("Введите токен: ").strip()
                        collect(login_data)
                    case -2:
                        login_data['login'] = str(input("Введите логин: ").strip())
                        login_data['password'] = str(input("Введите пароль: ").strip())
                        collect(login_data)
                    case _:
                        print("Такого варианта нет")
                        menu_auth()

    except Exception as e:
        error_log.add('menu_auth', e)


# Выход из аккаунта
def clean_exit():
    global login_vk
    login_vk = None

    clean_login_data()
    menu_auth()


# Инициализирует вход и чтение настроек, а так же создает папку с пользователем
def collect(config: login_data):
    global login_vk
    login_vk = LoginVK(config)

    global setting
    setting = Settings()

    global path_user
    path_user = set_path_user(setting.dump_path, login_vk.own_id, login_vk.name)

    makedirs(path_user, exist_ok=True)

    if not setting.show_off:
        menu_main()


# Парсер аргументов
def create_parser():
    pars = argparse.ArgumentParser()
    pars.add_argument('-t', '--token', type=str, help='Токен', nargs='?')
    pars.add_argument('-l', '--login', type=str, help='Логин', nargs='?')
    pars.add_argument('-p', '--password', type=str, help='Пароль писать в "" ', nargs='?')
    pars.add_argument('-sp', '--setpath', type=str, help='Название папки для сохранения', nargs='?')
    pars.add_argument('-sd', '--setdumpmethod', type=str, choices=['txt', 'offline', 'online'],
                      help='Метод сохранения данных, offline-фотографии доступны без интернета(самый долгий метод "Я предупредил")',
                      nargs='?')
    pars.add_argument('-slp', '--setlimitphoto', type=int, help='Лимит фотографий', nargs='?')
    pars.add_argument('-sld', '--setlimitdialog', type=int, help='Лимит диалогов', nargs='?')
    pars.add_argument('-si', '--setinterval', help='Добавляет интервалы между запросами, default=True',
                      action='store_true')
    pars.add_argument('-siv', '--setinvalue', type=int,
                      help='Время интервала выбирается рандомно из диапозона чисел default=[1, 10]', nargs='*')

    pars.add_argument('-shw', '--sethw', type=int, help='Устанавливает размеры фото default=[500, 650] (height and width)',
                      nargs='*')
    pars.add_argument('-srod', '--setrod', type=int, help='Как часто файл фотографий альбома будет делиться на части'
                                                          ' default=2(каждые 2000 фотографий', nargs='?')
    pars.add_argument('-su', '--saveuser', help='Сохранить пользователя', action='store_true')
    pars.add_argument('-ru', '--removeuser', help='Удалить пользователя', action='store_true')
    pars.add_argument('-m', '--method', type=int,
                      help='1 - Фотографии из всех диалогов\n 2 - Фотографии из опр. диалога \n 3 - Фото из плейлистов \n 4 - Плейлисты опр. пользователя \n 5 - Сохры всех друзей у которых открыты',
                      nargs='+')
    pars.add_argument('-u', '--user', type=int, help='id пользователя(ей) для методов 2,4', nargs='*')
    pars.add_argument('-os', '--onlysaved', help='(default:True) в методах 3-4, берётся только альбом с сохрами',
                      action='store_false')
    return pars


# Функции аргументов
def option_parser(argv):
    try:
        if not login_vk:
            if argv.token and not argv.login and not argv.password:
                login_data['token'] = argv.token
                collect(login_data)
            elif argv.login and argv.password and not argv.token:
                login_data['login'] = str(argv.login)
                login_data['password'] = str(argv.password)
                collect(login_data)
            else:
                raise Exception("Authorization data is not specified, or it is specified incorrectly")

        print("Auth success")

        setting.set_change_show(True)

        if (argv.setpath
                or argv.setdumpmethod
                or argv.setlimitphoto
                or argv.setlimitdialog
                or argv.saveuser
                or argv.removeuser
                or argv.setinterval
                or argv.setinvalue
                or argv.sethw
                or argv.setrod
                or argv.onlysaved):

            setting.check_err()

            if argv.setpath:
                setting.set_dump_path(argv.setpath)
            if argv.setdumpmethod:
                if argv.setdumpmethod == "txt":
                    setting.set_dump("dump_txt", True)
                elif argv.setdumpmethod == "offline":
                    setting.set_dump("dump_html_offline", True)
                    setting.set_dump("dump_html", False)
                else:
                    setting.set_dump("dump_html_offline", False)
                    setting.set_dump("dump_html", True)

            if argv.setlimitphoto:
                setting.set_limit_photo(argv.setlimitphoto)

            if argv.setlimitdialog:
                setting.set_limit_dialog(argv.setlimitdialog)

            if argv.setinterval:
                setting.set_dump("a_interval", False)

            if argv.setinvalue:
                setting.set_interval_values(argv.setinvalue)

            if argv.sethw:
                setting.set_height_width(argv.sethw[0], argv.sethw[1])

            if argv.setrod:
                setting.set_rod(argv.setrod)

            if argv.saveuser and not argv.removeuser:
                us = {
                    "name": login_vk.name,
                    "access_token": login_vk.access_token}
                accessToken.add(us)
            if argv.removeuser and not argv.saveuser:
                us = {
                    "name": login_vk.name,
                    "access_token": login_vk.access_token}
                accessToken.remove(us)
            if argv.onlysaved:
                setting.set_album_only_saved(argv.onlysaved)


        if argv.method:
            for m in argv.method:
                match m:
                    case 1:
                        print(f"\n")
                        get_dialogs_photo()
                    case 2:
                        if argv.user:
                            print(f"\n")
                            get_dialogs_photo(argv.user)
                    case 3:
                        print(f"\n")
                        get_photos_friend(0)
                    case 4:
                        if argv.user and len(argv.user) == 1:
                            print(f"\n")
                            get_photos_friend(argv.user)
                        else:
                            for i in argv.user:
                                get_photos_friend(i)
                    case 5:
                        print(f"\n")
                        get_photos_friends()
                    case _:
                        raise Exception("Wrong method selected")
        else:
            raise Exception("Method not specified -m [1;2;3;4;5]")
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
            menu_auth()
        else:
            parser = create_parser()
            option_parser(parser.parse_args(sys.argv[1:]))
        error_log.save_log()
    except Exception as e:
        error_log.add('colored', e)
    except KeyboardInterrupt:
        sys.exit()
    finally:
        error_log.save_log()
