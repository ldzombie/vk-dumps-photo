from modules.models import AccessToken


def add(user_id, name, token):
    if AccessToken.get_or_none(access_token=token) is None:
        AccessToken.get_or_create(user_id=user_id, name=name, access_token=token)


def remove(user_id, user_name):
    try:
        q = AccessToken.delete().where(AccessToken.user_id == user_id & AccessToken.name == user_name)
        q.execute()
        return True
    except Exception:
        return False


def remove_token(token: str):
    try:
        q = AccessToken.delete().where(AccessToken.access_token == token)
        q.execute()
        return True
    except Exception:
        return False


def none_or_create(user_id, name, token):
    if AccessToken.get_or_none(user_id=user_id, name=name) is None:
        print("fdfd")
        add(user_id, name, token)


def get_token_id(index: int):
    return AccessToken.get_by_id(index).access_token


def length():
    return len(AccessToken.select().count())


def get_users():
    msg = ''
    for user in AccessToken.select():
        msg += f"{user['id']} - {user['name']}"
    return msg

