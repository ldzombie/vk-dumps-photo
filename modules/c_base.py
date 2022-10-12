from telebot import types

from modules.Strings import Texts, RATES
from modules.models import User
from modules import config


#  Возвращает тариф пользователя в текстовом виде
def get_account_rate(user_id: int, string: bool = True):
    try:
        rate = User.get(User.external_id == user_id).account_rate
        return RATES[rate] if string else rate
    except Exception as e:
        print(e)


#  Проверяет пользователя на права админа по тарифу
def check_admin(user_id: int):
    if get_account_rate(user_id, False) == 99999:
        return True
    elif user_id == config.ADMIN_ID:
        rate = User.get(User.external_id == user_id).account_rate
        if not rate == list(RATES.keys())[list(RATES.values()).index("Админ")]:
            q = (User
                 .update({User.account_rate: 99999})
                 .where(User.external_id == user_id))
            q.execute()  # Execute the query, returning number of rows updated.
        return True
    else:
        return False


#  Устанавливает пользователю тариф
def set_rate(user_id: int, s_rate: int):
    try:
        if User.get_or_none(User.external_id == user_id) is not None:
            q = (User.update({User.account_rate: s_rate})
                 .where(User.external_id == user_id))
            q.execute()
            return True
        return False
    except Exception as e:
        print(e)
        return False


#  Выводит информацию по отдельному пользователю
#  С возможностью управления
def get_user_prof(chat_id, user_id, first_name):
    inlmarkp = types.InlineKeyboardMarkup()
    inl_rate = types.InlineKeyboardButton("Изменить тариф", callback_data=f"u_rate_{user_id}")
    inlmarkp.add(inl_rate)
    config.bot.send_message(chat_id, Texts['get_user'].format(
        first_name,
        get_account_rate(user_id)), parse_mode='html', reply_markup=inlmarkp)


#  Возвращает объект с данными о пользователе
def get_user(user_id: int):
    return config.bot.get_chat_member(User.get(User.external_id == user_id).chat_id, user_id).user


#  Список пользователей с кнопками для получения подробной информации по пользователю
#  Стандартно выводиться 6 пользователей
def get_users(chat_id, count_start=0, step=2):
    try:
        #  Делаем запрос из таблицы пользователей чей id > переменной начала отсчета(count_start)
        #  и меньше или равен сумме шага и начала отсчета
        query = User.select().where((User.id > count_start) & (User.id <= count_start+step)).dicts()
        msg = Texts['list_users']
        buttons = []

        if query is None:
            raise Exception("Пользователи не найдены")

        for row in query:
            u_name = get_user(row['external_id']).first_name
            u_ext_id = row['external_id']
            u_id = row['id']

            #  Добавляем информацию о пользователе в список, и добавляем кнопку для этого пользователя
            if count_start < u_id <= (count_start+step):
                msg += f"{u_id}. {u_name} - {get_account_rate(row['external_id'])} - {u_ext_id} \n"
                buttons.append(types.InlineKeyboardButton(u_id, callback_data=f"u_get_{u_ext_id}"))
            else:
                break
        lg = len(buttons)
        all_user = User.select().count()
        buttons = list_separator(buttons, n=step)
        if lg == step:
            #  Если список получен с 0, то добавляем кнопку, чтобы получить следующий список пользователей
            if count_start == 0 and not lg == all_user:
                buttons.append([types.InlineKeyboardButton("next", callback_data=f"u_get_n_{count_start + step}")])
            #  Иначе если общее количество пользователей меньше суммы начала отсчета и шага
            #  добавляем 2 кнопки для пролистывания вперед и назад
            elif User.select().count() > count_start + step:
                buttons.append([types.InlineKeyboardButton("back", callback_data=f"u_get_b_{count_start - step}"),
                                types.InlineKeyboardButton("next", callback_data=f"u_get_n_{count_start + step}")])
            #  В других случаях это последний список пользователей, добавляем кнопку назад
        elif (all_user < count_start + step) and ((count_start - step) > 0):
            buttons.append([types.InlineKeyboardButton("back", callback_data=f"u_get_b_{count_start - step}")])

        #  Располагаем кнопки по строкам в inlineMarkup
        inlm = types.InlineKeyboardMarkup([row for row in buttons])

        if msg is not None:
            config.bot.send_message(chat_id, msg, parse_mode='html', reply_markup=inlm)

    except Exception as e:
        print(e)


#  Разбивает список по частям, в каждом по n элементов
def list_separator(lst, n=6):
    return [lst[i:i + n] for i in range(0, len(lst), n)]
