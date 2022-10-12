from telebot import types

from modules import c_base
from modules.Strings import Buttons, RATES


# welcome
def welcome_menu(user_id: int = 0):
    try:
        if user_id == 0:
            raise Exception("user_id == 0")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        m_info = types.KeyboardButton(Buttons['button_info'])
        m_my_account = types.KeyboardButton(Buttons['button_my_rate'])
        m_auth = types.KeyboardButton(Buttons['button_start'])

        if c_base.check_admin(user_id):
            m_admin = types.KeyboardButton(Buttons['button_admin'])
            markup.add(m_auth, m_admin)
        else:
            markup.add(m_auth, row_width=1)

        markup.add(m_my_account, m_info, row_width=2)
        return markup
    except Exception as e:
        print(f"welcome_menu - {e}")


# admin menu
def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    m_list_users = types.KeyboardButton(Buttons['button_list_users'])
    back = types.KeyboardButton(Buttons["button_back"])
    markup.add(m_list_users, back, row_width=2)
    return markup


# Информация
def info_and_about_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(Buttons['button_about'])
    item2 = types.KeyboardButton(Buttons['button_support'])
    back = types.KeyboardButton(Buttons['button_back'])
    markup.add(item1, item2, row_width=2)
    markup.add(back)
    return markup


#  Мой тариф
def rate_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(Buttons['button_subs'])
    back = types.KeyboardButton(Buttons["button_back"])
    markup.add(item1, back, row_width=2)
    return markup


#  Поддержка
def support_inline_menu():
    inm = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("*тык*", url="t.me/mytfrgyhbot_support")
    inm.add(item1)
    return inm


# start inline menu
def start_inline_menu():
    markupInline = types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(Buttons['inline_lp'], callback_data="auth_login"),
                types.InlineKeyboardButton(Buttons['inline_token'], callback_data="auth_token")
            ],
        ], row_width=2
    )
    return markupInline


# Используется при команде rate когда не указали тариф
def user_rate_inline_menu(user_id):
    try:
        if user_id == 0:
            raise Exception("user_id == 0")

        inlmarku = types.InlineKeyboardMarkup()
        for key, value in RATES.items():
            inlmarku.add(types.InlineKeyboardButton(text=value, callback_data=f"u_rate_{user_id}_{key}"))
        return inlmarku
    except Exception as e:
        print(f"user_rate_inline_menu - {e}")


def out_func():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton(Buttons['button_back'])
    markup.add(back)
    return markup


def m_main():
    inm = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Методы")
    item2 = types.KeyboardButton("Настройки")
    item3 = types.KeyboardButton("Выход")
    inm.add(item1, item2)
    inm.add(item3)
    return inm


def methods_inline(user_id):
    markupInline = types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton("1", callback_data=f"a_m_1_{user_id}"),
                types.InlineKeyboardButton("2", callback_data=f"a_m_2_{user_id}"),
                types.InlineKeyboardButton("3", callback_data=f"a_m_3_{user_id}"),
                types.InlineKeyboardButton("4", callback_data=f"a_m_4_{user_id}"),
                types.InlineKeyboardButton("5", callback_data=f"a_m_5_{user_id}")
            ],
        ],
        row_width=2
    )
    return markupInline