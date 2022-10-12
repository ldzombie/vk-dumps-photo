import peewee
import sys
sqlite_db = peewee.SqliteDatabase(f'{sys.path[1]}/app.db', pragmas={
    'journal_mode': "wal",
    'cache_size': -1024 * 64
})


class BaseModel(peewee.Model):
    class Meta:
        database = sqlite_db


class User(BaseModel):
    external_id = peewee.BigIntegerField(unique=True)
    chat_id = peewee.BigIntegerField(unique=True)
    account_rate = peewee.BigIntegerField(unique=False)


class AccessToken(BaseModel):
    user_id = peewee.BigIntegerField(unique=False)
    name = peewee.TextField(unique=False)
    access_token = peewee.TextField(unique=True)


if __name__ == '__main__':
    sqlite_db.create_tables([User, AccessToken])
