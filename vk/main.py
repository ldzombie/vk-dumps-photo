import json
from os import makedirs
from os.path import join, exists

from modules.Strings import Texts
from vk.modules.c_auth import LoginVK, clean_login_data, login_data, set_path_user
from vk.modules.c_error import ErrorLog
from vk.modules.c_settings import Settings
from vk.modules.oth_function import *
from modules.config import bot
from modules.menus import out_func

# globals

json_albums = []

error_log = ErrorLog()
login_vk = {}
path_user = {}
setting = {}


# Фотографии из диалогов
def get_dialogs_photo(chat_id, user_id, users_ids: list = None):
    try:
        if setting[user_id].dump_html or setting[user_id].dump_html_offline:
            imgs = ""
        if setting[user_id].dump_txt:
            urls = []
            dialogs = []
        if users_ids is not None:
            all_dialogs = []
            for i in range(len(users_ids)):
                test = login_vk[user_id].vk.messages.getConversationsById(peer_ids=users_ids[i])
                all_dialogs += test["items"]
        else:
            if setting[user_id].limit_dialog == 0 or setting[user_id].limit_dialog > 200:
                test = login_vk[user_id].vk.messages.getConversations(count=200)  # Получаем диалоги через токен
                all_dialogs = test["items"]
                print(test)

                if len(all_dialogs) == 200:
                    # Нужно, чтобы получить все диалоги, если их больше 200
                    offset = 200  # сдвиг начала отсчёта
                    while True:
                        setting[user_id].intervals()
                        fo1 = login_vk[user_id].vk.messages.getConversations(count=200, offset=offset)
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
                all_dialogs = login_vk[user_id].vk.messages.getConversations(count=setting[user_id].limit_dialog)["items"]

        num = len(all_dialogs)
        # Количество диалогов
        bot.send_message(chat_id, Texts['all_dialogs'].format(num), parse_mode='html')
        bot.send_message(chat_id, Texts['m_1_start'].format(login_vk[user_id].name, login_vk[user_id].own_id),
                         parse_mode='html')

        path_dialog = f'{path_user[user_id]}/dialog'

        for dialog in all_dialogs:  # Идем по списку
            if users_ids is not None:
                idd = dialog["peer"]["id"]
                peer_type = dialog['peer']['type']  # Информация о диалоге
            else:
                idd = dialog["conversation"]["peer"]["id"]  # Вытаскиваем ID человека с диалога
                peer_type = dialog['conversation']['peer']['type']  # Информация о диалоге (конференция это или человек)

            if peer_type == "user":  # Ставим проверку конференции
                if idd > 0:  # Ставим проверку на группы

                    b = login_vk[user_id].vk.users.get(user_ids=idd)[0]  # Получаем информацию о человеке

                    fio = f'{b["first_name"]} {b["last_name"]}'

                    bot.send_message(chat_id, Texts['m_1'].format(idd, fio), parse_mode='html')

                    if setting[user_id].limit_photo <= 200 and not setting[user_id].limit_photo == 0:
                        setting[user_id].intervals()
                        fo = login_vk[user_id].vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo',
                                                                                 start_from=0,
                                                                                 count=setting[user_id].limit_photo,
                                                                                 preserve_order=1,
                                                                                 max_forwards_level=45)
                        a_photo = fo["items"]

                    else:
                        fo = login_vk[user_id].vk.messages.getHistoryAttachments(peer_id=idd, media_type='photo',
                                                                                 start_from=0,
                                                                                 count=200,
                                                                                 preserve_order=1,
                                                                                 max_forwards_level=45)
                        a_photo = fo["items"]

                        if len(a_photo) == 200:
                            offset = fo["next_from"]  # сдвиг начала отсчёта
                            while True:
                                if setting[user_id].limit_photo == 0:
                                    count = 200
                                else:
                                    count = setting[user_id].limit_photo - len(a_photo)
                                    if count >= 200:
                                        count = 200
                                    if count == 0 or count < 0:
                                        break
                                setting[user_id].intervals()
                                fo1 = login_vk[user_id].vk.messages.getHistoryAttachments(peer_id=idd,
                                                                                          media_type='photo',
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
                                if length == 200 and length_all < setting[user_id].limit_photo or length == 200 and setting[user_id].limit_photo == 0:
                                    offset = fo1["next_from"]
                                else:
                                    break

                    if len(a_photo) == 0:
                        continue

                    for i in a_photo:  # Идем по списку вложений
                        for j in i["attachment"]["photo"]["sizes"]:
                            if setting[user_id].check_sizes(j["height"]) or setting[user_id].check_sizes(j["width"]):  # Проверка размеров
                                url = j["url"]  # Получаем ссылку на изображение
                                if setting[user_id].dump_txt:
                                    urls.append(url)
                                if setting[user_id].dump_html and not setting[user_id].dump_html_offline:
                                    imgs += f'<img class="photos" src="{url}" alt="Не удалось загрузить" ' \
                                            f'title="Найдено в диалоге - vk.com/id{idd}">'  # Сохраняем в переменную
                                if setting[user_id].dump_html_offline:
                                    base = get_as_base64(url)
                                    imgs += f'<img class="photos" src="data:image/png;base64,{base}" ' \
                                            f'alt="Не удалось загрузить " title="Найдено в альбоме - {idd}">'
                                break  # чтобы не сохраняло одинаковые фотографии разного размера
                    if setting[user_id].dump_html or setting[user_id].dump_html_offline:
                        try:
                            makedirs(f'{path_dialog}', exist_ok=True)
                            with (open(f'{path_dialog}/{idd} - {fio}.html', 'w+', encoding="utf8") as save_photo,
                                  open(f'{path}/photo_pre.html', 'r', encoding="utf8") as photo_pre):
                                save_photo.write(photo_pre.read() + imgs)
                        except Exception as e:
                            error_log.add("get_dialogs_photo save_photo", e)

                        imgs = ""
                    if setting[user_id].dump_txt:
                        dialogs.append({'name': '_'.join(fio), 'photos': urls})
                        urls = []
                    bot.send_message(chat_id, Texts['m_1_end'].format(len(a_photo)), parse_mode='html')
                else:
                    continue
            else:
                continue

        if setting[user_id].dump_txt:
            file_name = 'dialogs.json'

            with open(join(f'{path_dialog}', file_name), 'w') as alb_file:
                json.dump(dialogs, alb_file)
        bot.send_message(chat_id, Texts['m_1_final'],
                         parse_mode='html',
                         reply_markup=out_func())
    except Exception as e:  # Исключения ошибок
        error_log.add('get_dialogs_photo', e)
        print(f"1 - {e}")


# Фотографии из плейлистов пользователя по id
def get_photos_friend(chat_id, user_id, user_vk_id: int, onlySaved: bool = True):
    try:
        global json_albums

        if user_vk_id == 0:
            user_vk_id = login_vk[user_id].own_id
            path_albums = f'{path_user[user_id]}/albums'
        else:
            user = login_vk[user_id].vk.users.get(user_ids=user_vk_id)[0]
            fio = f'{user["first_name"]} {user["last_name"]}'
            path_user_friend = f'{path}/{user_id}/dump/{user_vk_id} - {fio}'
            path_albums = f'{path_user_friend}/albums'

        if onlySaved:
            albums = login_vk[user_id].vk.photos.getAlbums(owner_id=user_vk_id, album_ids="-15")
        else:
            albums = login_vk[user_id].vk.photos.getAlbums(owner_id=user_vk_id, need_system=1)

        num = albums["count"]  # Количество альбомов

        bot.send_message(chat_id, Texts['m_3_all'].format(num), parse_mode='html')

        if num == 0:
            raise Exception

        bot.send_message(chat_id, Texts['m_3_start'])

        for album in albums["items"]:
            idd = album["id"]
            title = album["title"]
            size = album["size"]
            if size == 0:
                continue

            bot.send_message(chat_id, f"{title} - Фото: {size}")

            a_photos = get_album_photo(user_id, user_vk_id, idd, size, path_albums, title)

            bot.send_message(chat_id, Texts['m_1_end'].format(a_photos), parse_mode='html')

        if setting[user_id].dump_txt:
            with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                json.dump(json_albums, alb_file)
            json_albums = []
        bot.send_message(chat_id, Texts['m_3_end'], parse_mode='html', reply_markup=out_func())
    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friend', e)
        print(e)


# Фотографии из плейлистов друзей с открытыми сохрами
def get_photos_friends(chat_id, user_id, onlySaved: bool = True):
    global json_albums
    try:
        friends = login_vk[user_id].vk.friends.get(fields="1", order="hints", name_case="nom", count=250)

        bot.send_message(chat_id, Texts['m_count_users'].format(str(friends['count'])), parse_mode='html')

        for friend in friends['items']:
            friend_id = friend['id']
            try:
                if onlySaved:
                    albums = login_vk[user_id].vk.photos.getAlbums(owner_id=friend_id, album_ids="-15")
                else:
                    albums = login_vk[user_id].vk.photos.getAlbums(owner_id=friend_id, album_ids="-15", need_system=1)

                if albums['count'] == 0 or not albums['items'][0]['id'] == -15:
                    continue
            except Exception as e:
                error_log.add("get_photos_friends onlySaved", e)
                continue

            friend_fio = f'{friend["first_name"]} {friend["last_name"]}'
            path_user_friend = f'{path}/{user_id}/dump/{friend_id} - {friend_fio}'
            path_albums = f'{path_user_friend}/albums'

            idd = albums['items'][0]['id']
            title = albums['items'][0]["title"]
            size = albums['items'][0]["size"]

            # если файл с этим альбомом же существует, то альбом пропускается
            if size == 0 or exists(f"{path_albums}/{title}-0.html"):
                continue

            bot.send_message(chat_id, Texts['m_3_start'] + friend_fio)
            bot.send_message(chat_id, f"{title} - Фото: {size}")

            a_photos = get_album_photo(user_id, friend_id, idd, size, path_albums, title)

            bot.send_message(chat_id, Texts['m_1_end'].format(a_photos), parse_mode='html')

            if setting[user_id].dump_txt:
                with open(join(f'{path_albums}/', 'albums.json'), 'w') as alb_file:
                    json.dump(json_albums, alb_file)
                json_albums = []
        bot.send_message(chat_id, Texts['m_3_end'], reply_markup=out_func())

    except Exception as e:  # Исключения ошибок
        error_log.add('get_photos_friends', e)
        print(e)


# Метод для получения всех фотографий из альбома
def get_album_photo(user_id, user_vk_id: int, album_id: int, siz: int, path_albums: str, title: str) -> int:
    try:
        cc, num, al_size = 1, 0, 0

        if setting[user_id].limit_photo == 0 or setting[user_id].limit_photo > 1000:
            al_photos = login_vk[user_id].vk.photos.get(owner_id=user_vk_id,
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
                    if setting[user_id].limit_photo == 0:
                        count = siz - len(al_photos)
                    else:
                        count = setting[user_id].limit_photo - len(al_photos)
                        if count <= 0:
                            break

                    if count > 1000:
                        count = 1000
                    if count <= 0:
                        break

                    setting[user_id].intervals()
                    fo1 = login_vk[user_id].vk.photos.get(owner_id=user_vk_id,
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

                    if cc % setting[user_id].s_rod == 0:
                        save_file_html(user_id,al_photos, album_id, path_albums, f'{title}-{num}')
                        num += 1
                        siz -= len(al_photos)
                        al_photos = []

                    if siz > len(al_photos) and (len(al_photos) < setting[user_id].limit_photo or setting[user_id].limit_photo == 0):
                        offset = al_size
                    else:
                        break

            if len(al_photos) > 0:
                save_file_html(al_photos, album_id, path_albums, f'{title}-{num}')
        else:
            al_photos = login_vk[user_id].vk.photos.get(owner_id=user_vk_id,
                                                        album_id=album_id,
                                                        photo_sizes=1,
                                                        rev=1,
                                                        count=setting[user_id].limit_photo)["items"]
            al_size += len(al_photos)
            save_file_html(al_photos, album_id, path_albums, f'{title}-0')
        return al_size
    except Exception as e:
        error_log.add("get_album_photo", e)


# Проходит по всем фотографиям и находит подходящий размер фото, после сохраняет в файл
def save_file_html(user_id, photos: list, idd: str, path_albums: str, title: str):
    try:
        global json_albums

        l_urls = []
        l_imgs = ""

        for i in photos:  # Идем по списку вложений
            for j in i["sizes"]:
                if setting[user_id].check_sizes(j["height"]) or setting[user_id].check_sizes(j["width"]):  # Проверка размеров
                    url = j["url"]  # Получаем ссылку на изображение
                    if setting[user_id].dump_txt:
                        l_urls.append(url)
                    if setting[user_id].dump_html and not setting[user_id].dump_html_offline:
                        l_imgs += f'<img class="photos" src="{url}" alt="Не удалось загрузить" ' \
                                  f'title="Найдено в альбоме - {idd}">'  # Сохраняем в переменную
                    if setting[user_id].dump_html_offline:
                        base = get_as_base64(url)
                        l_imgs += f'<img class="photos" src="data:image/png;base64,{base}" alt="Не удалось загрузить" ' \
                                  f'title="Найдено в альбоме - {idd}">'
                    break  # чтобы не добавляло одинаковых фото

        if setting[user_id].dump_html or setting[user_id].dump_html_offline:
            try:
                makedirs(f'{path_albums}', exist_ok=True)
                with (open(f'{path_albums}/{title}.html', 'w+', encoding="utf8") as save_photo,
                      open(f'{path}/photo_pre.html', 'r', encoding="utf8") as photo_pre):
                    save_photo.write(photo_pre.read() + l_imgs)

            except Exception as e:
                error_log.add("save_file_html", e)
        if setting[user_id].dump_txt:
            json_albums.append({'name': "_".join(title.split(' ')), 'photos': l_urls})
            print(len(l_urls))
    except Exception as e:
        error_log.add("save_file", e)


def clean_exit(user_id):
    global login_vk
    login_vk.pop(user_id)

    clean_login_data()


def is_auth(user_id):
    if len(login_vk) == 0:
        return False
    elif user_id in login_vk:
        return True


# Инициализирует вход и чтение настроек, а так же создает папку с пользователем
def collect(config: login_data, user_id):
    global login_vk
    login_vk[user_id] = LoginVK(config, user_id)
    print(login_vk[user_id])

    if not exists(f'{path}/{user_id}'):
        makedirs(f'{path}/{user_id}')
    if not exists(f'{path}/photo_pre.html'):
        create_photo_pre()

    global setting
    setting[user_id] = Settings(user_id)

    global path_user
    path_user[user_id] = set_path_user(user_id, setting[user_id].dump_path, login_vk[user_id].own_id, login_vk[user_id].name)

    makedirs(path_user[user_id], exist_ok=True)
