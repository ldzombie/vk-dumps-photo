import time

from modules import c_base, menus, c_access_token

from modules.config import bot

from modules.models import User, AccessToken
from modules.Strings import Buttons, Texts, RATES

# Сообщение при команде /start
from vk import main
from vk.modules.c_auth import login_data


@bot.message_handler(commands=['start'])
def welcome(message):
    #  Если пользователь не существует в базе, то он создается
    if User.get_or_none(external_id=message.from_user.id) is None:
        User.create(external_id=message.from_user.id, chat_id=message.chat.id, account_rate=0)

    #  Отправка стикера
    sti = open('static/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)

    bot.send_message(message.chat.id, Texts['welcome'].format(message.from_user, bot.get_me()), parse_mode='html',
                     reply_markup=menus.welcome_menu(message.from_user.id))


# Команды для админа
@bot.message_handler(commands=['list', 'rate', 'getuser'])
def admin_command(message):
    if message.chat.type == 'private' and c_base.check_admin(message.from_user.id):
        match message.text.split():
            case ["/list"]:
                c_base.get_users(message.chat.id)
            case ("/rate", a, b):
                try:
                    if c_base.set_rate(a, b):
                        bot.send_message(message.chat.id, Texts['rate_set']
                                         .format(a, RATES[int(b)]), parse_mode='html')
                    else:
                        bot.send_message(message.chat.id, Texts['user_not_exists'].format(a), parse_mode='html')
                except Exception as e:
                    print(e)
            case ("/getuser", a):
                try:
                    c_base.get_user_prof(message.chat.id, a, c_base.get_user(a).first_name)

                except Exception as e:
                    print(e)
            case _:
                bot.send_message(message.chat.id, Texts['unknown'])
    else:
        bot.send_message(message.chat.id, Texts['not_permissions'], parse_mode='html')


# Обработчик обычных кнопок
@bot.message_handler(content_types=['text'])
def bot_mes(message):
    if message.chat.type == 'private':

        if User.get_or_none(external_id=message.from_user.id) is None:
            User.create(external_id=message.from_user.id, chat_id=message.chat.id, account_rate=0)

        match message.text:
            case "📚Информация":  # info

                bot.send_message(chat_id=message.chat.id,
                                 text=Buttons['button_info'],
                                 parse_mode='html',
                                 reply_markup=menus.info_and_about_menu())

            case "💾О боте":  # о боте

                bot.send_message(chat_id=message.chat.id,
                                 text=Texts['about_bot'],
                                 parse_mode='html',
                                 reply_markup=menus.info_and_about_menu())

            case "Мой тариф":  # rate

                bot.send_message(message.chat.id, text=Texts['get_rate'].format(
                    c_base.get_account_rate(message.from_user.id)
                ), parse_mode='html', reply_markup=menus.rate_menu())

            case "◀️Назад" | "Выход" as text:  # back
                if main.is_auth(message.from_user.id):
                    if text == Buttons['button_exit']:
                        main.clean_exit(message.from_user.id)
                        bot.send_message(message.chat.id,
                                         Buttons['button_exit'],
                                         parse_mode='html',
                                         reply_markup=menus.welcome_menu(message.from_user.id))
                    else:
                        bot.send_message(message.chat.id, Texts['auth_info'].format(main.login_vk[message.from_user.id].name),
                                         parse_mode='html',
                                         reply_markup=menus.m_main())
                else:
                    bot.send_message(message.chat.id,
                                     Buttons['button_back'],
                                     parse_mode='html',
                                     reply_markup=menus.welcome_menu(message.from_user.id))

            case "Подписки":  # subs
                c_base.check_admin(message.from_user.id)

            case "Админ панель":  # admin panel
                if not c_base.check_admin(message.from_user.id):
                    bot.send_message(message.chat.id, Texts['not_permissions'])
                else:

                    bot.send_message(message.chat.id,
                                     Buttons['button_admin'],
                                     parse_mode='html',
                                     reply_markup=menus.admin_menu())
            case "Все пользователи":
                if not c_base.check_admin(message.from_user.id):
                    bot.send_message(message.chat.id,
                                     Texts['not_permissions'],
                                     parse_mode='html')
                else:
                    c_base.get_users(message.chat.id)

            case "*️⃣Поддержка":

                bot.send_message(message.chat.id,
                                 Buttons['button_support'], parse_mode='html',
                                 reply_markup=menus.support_inline_menu())

            case "Начать🔎":  # start

                bot.send_message(message.chat.id,
                                 Texts['m_start'],
                                 reply_markup=menus.start_inline_menu())
            case "Аккаунт":
                if main.is_auth(message.from_user.id):
                    bot.send_message(message.chat.id, Texts['auth_info'].format(main.login_vk[message.from_user.id].name),
                                     parse_mode='html',
                                     reply_markup=menus.m_main())
                else:
                    bot.send_message(message.chat.id,
                                     Buttons['button_back'],
                                     parse_mode='html',
                                     reply_markup=menus.welcome_menu(message.from_user.id))
            case "Методы":
                if main.is_auth(message.from_user.id):
                    bot.send_message(message.chat.id,
                                     Texts['methods'],
                                     parse_mode='html',
                                     reply_markup=menus.methods_inline(message.from_user.id))
                else:
                    bot.send_message(message.chat.id,
                                     Buttons['button_back'],
                                     parse_mode='html',
                                     reply_markup=menus.welcome_menu(message.from_user.id))
            # case "Настройки":
            case _:
                bot.send_message(message.chat.id, Texts['unknown'])


# Обработчик inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        print(call.data.split("_"))
        match call.data.split("_"):

            # Выбор тарифов
            case "u", "rate", a:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=Texts['select_rate'],
                                      parse_mode='html',
                                      reply_markup=menus.user_rate_inline_menu(a))
            # Установка тарифа (b) пользователю с external_id (a)
            case "u", "rate", a, b:
                if c_base.set_rate(a, b):
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          text=Texts['rate_set'].format(c_base.get_user(a).first_name, RATES[int(b)]),
                                          parse_mode='html')
            # Следующие 3 для списка пользователей
            case "u", "get", a:
                b = c_base.get_user(a).first_name
                bot.delete_message(call.message.chat.id, call.message.message_id)
                c_base.get_user_prof(call.message.chat.id, a, b)
            case "u", "get", "n", a:  # next
                bot.delete_message(call.message.chat.id, call.message.message_id)
                c_base.get_users(call.message.chat.id, count_start=int(a))

            case "u", "get", "b", a:  # back
                bot.delete_message(call.message.chat.id, call.message.message_id)
                c_base.get_users(call.message.chat.id, count_start=int(a))

            case "a", "m", a, b:
                match int(a):
                    case 1:
                        main.get_dialogs_photo(chat_id=call.message.chat.id, user_id=int(b))
                    case 2:
                        msg = bot.send_message(int(login_data['chat_id']), Texts['w_user_id'])
                        bot.register_next_step_handler(msg, get_ids, 2, int(b))
                    case 3:
                        main.get_photos_friend(user_id=int(b), chat_id=call.message.chat.id, user_vk_id=0)
                    case 4:
                        msg = bot.send_message(int(login_data['chat_id']), Texts['w_user_id'])
                        bot.register_next_step_handler(msg, get_ids, 4, int(b))
                    case 5:
                        main.get_photos_friends(user_id=int(b), chat_id=call.message.chat.id)

            case "auth", "token":
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=Texts['auth_token'],
                                      reply_markup=None)
                msg = bot.send_message(call.message.chat.id, Texts['w_token'])
                bot.register_next_step_handler(msg, auth_token)
            case "auth", "login":
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=Texts['auth_login'],
                                      reply_markup=None)
                msg = bot.send_message(call.message.chat.id, Texts['w_login'])
                bot.register_next_step_handler(msg, auth_login, 0)

            case _:
                bot.send_message(call.message.chat.id, Texts['unknown'])

    except Exception as e:
        print(f"callback_inline - {e}")


def auth_login(message, arg):
    if arg == 0:
        login_data['token'] = ""
        login_data['login'] = message.text
        msg = bot.send_message(message.chat.id, Texts['w_pass'])
        bot.register_next_step_handler(msg, auth_login, 1)
    elif arg == 1:
        login_data['password'] = message.text
        login_data['chat_id'] = message.chat.id
        main.collect(login_data, message.from_user.id)

        time.sleep(5)


def get_ids(message, val, user_id):
    users = list(map(int, message.text.strip().split()))
    if val == 2:
        main.get_dialogs_photo(chat_id=message.chat.id, user_id=user_id, users_ids=users)
    elif val == 4:
        for i in users:
            main.get_photos_friend(user_id=user_id, chat_id=message.chat.id, user_vk_id=i)


def auth_token(message):
    login_data['login']=""
    login_data['password']=""
    login_data['token'] = message.text
    login_data['chat_id'] = message.chat.id
    try:
        main.collect(login_data, message.from_user.id)
    except Exception as e:
        print(e)
        bot.send_message(login_data['chat_id'], Texts['auth_failed'], reply_markup=menus.start_inline_menu())


# Чтобы бот не завершал работу после запуска
bot.polling(none_stop=True)
