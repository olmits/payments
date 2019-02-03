import os
from peewee import *

db_proxy = Proxy()


class PaymentsDB(Model):
    class Meta:
        database = db_proxy

    amount = DoubleField()
    currency = CharField()
    description = CharField()
    update_date = DateTimeField()
    payment_id = CharField()
    status = CharField()

    def __str__(self):
        return f"{self.payment_id}; Currency: {self.currency}; Amount: {self.amount}; Description: {self.status}"

    @staticmethod
    def update_status(status, payment_id):
        query = PaymentsDB.select().where(PaymentsDB.payment_id == payment_id)
        if query.exists():
            query = query.first()
            query.status = status
            query.save()


if 'HEROKU' in os.environ:
    import urllib.parse, psycopg2

    urllib.parse.uses_netloc.append('postgres')
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    db = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname,
                            port=url.port)
    db_proxy.initialize(db)
else:
    db = SqliteDatabase('payments.db')
    db_proxy.initialize(db)

if __name__ == '__main__':
    db_proxy.connect()
    db_proxy.create_tables([PaymentsDB], safe=True)
    db_proxy.close()
