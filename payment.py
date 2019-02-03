import hashlib
import requests
from datetime import datetime
from db_model import PaymentsDB
from app import app


class Payment:

    secret_key = "SecretKey01"
    subclasses = {}
    payment_num = 1

    def __init__(self, amount, currency, description):
        self.amount = str.replace(amount, ',', '.')
        self.currency = currency
        self.description = description
        self.shop_id = '5'
        self.shop_order_id = '4268'
        self.payment_id = "%s%i_%s" % (currency,
                                       Payment.payment_num,
                                       datetime.strftime(datetime.now(), "%d%m%y%H%M%S")
                                       )
        Payment.update_db(self)

    @classmethod
    def form_processing(cls, form):
        return cls(form['amount'], form['currency'], form['description'])

    @classmethod
    def payment_subclass(cls, currency_type):
        def decorator(subclass):
            cls.subclasses[currency_type] = subclass
            return subclass
        return decorator

    @classmethod
    def get_subclass(cls, currency_type):
        return cls.subclasses[currency_type]

    @staticmethod
    def create_sign(required_data, required_keys):
        required_data = ':'.join([required_data[value] for value in sorted(required_keys)])
        required_data += Payment.secret_key
        sign = hashlib.sha256(required_data.encode('utf-8')).hexdigest()
        return sign

    def update_db(self):
        PaymentsDB.create(
            amount=self.amount,
            currency=self.currency,
            description=self.description,
            update_date=datetime.now(),
            payment_id=self.payment_id,
            status='Unknown'
        )

        Payment.payment_num += 1


@Payment.payment_subclass('978')
class PayPageProcessing(Payment):

    keys_required = ('amount', 'currency', 'shop_id', 'shop_order_id')
    action_url = 'https://pay.piastrix.com/ru/pay'

    def __init__(self, amount, currency, description):
        super().__init__(amount, currency, description)
        self.sign = Payment.create_sign(self.__dict__, self.keys_required)

    def request(self):
        result = dict(zip(('data', 'method', 'url'), (self.__dict__, 'post', self.action_url)))
        return result


@Payment.payment_subclass('840')
class BillProcessing(Payment):

    keys_required = ('shop_amount', 'shop_currency', 'shop_id', 'shop_order_id', 'payer_currency')
    action_url = 'https://core.piastrix.com/bill/creat'

    def __init__(self, amount, currency, description):
        super().__init__(amount, currency, description)
        self.rename_attribute('amount', 'shop_amount')
        self.rename_attribute('currency', 'shop_currency')
        self.payer_currency = currency
        self.sign = Payment.create_sign(self.__dict__, self.keys_required)

    def rename_attribute(self, old_name, new_name):
        self.__dict__[new_name] = self.__dict__.pop(old_name)

    def request(self):
        try:
            result = requests.post(self.action_url, json=self.__dict__)
            app.logger.info(f'{self.__class__.__name__} Request success - id: {self.payment_id}')
            return result.json()
        except requests.exceptions.RequestException as problem:
            app.logger.debug(f'{self.__name__} Request exception: {problem}')


@Payment.payment_subclass('643')
class InvoiceProcessing(Payment):

    keys_required = ('amount', 'currency', 'payway', 'shop_id', 'shop_order_id')
    action_url = 'https://core.piastrix.com/invoice/create'

    def __init__(self, amount, currency, description):
        super().__init__(amount, currency, description)
        self.payway = 'payeer_rub'
        self.sign = Payment.create_sign(self.__dict__, self.keys_required)

    def request(self):
        try:
            result = requests.post(self.action_url, json=self.__dict__)
            app.logger.info(f'{self.__class__.__name__} Request success - id: {self.payment_id}')
            return result.json()
        except requests.exceptions.RequestException as problem:
            app.logger.debug(f'{self.__name__} Request exception: {problem}')
