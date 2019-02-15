from flask import render_template, request, flash, g

from webapp import app
from webapp.payment import Payment
from webapp.db_model import PaymentsDB, db_proxy
from webapp.paypage_funcs import currency_to_func_map as payment_map


@app.before_request
def before_request():
    g.db = db_proxy
    g.db.connect()


@app.route('/')
@app.route('/result', methods=['POST', 'GET'])
def get_output():
    if request.method == 'POST':

        form = request.form
        user_currency = form.get('currency')
        get_payment = Payment.create_payment(user_currency, form)
        payment_data = get_payment.request()

        if not payment_data.get('data') is None:
            PaymentsDB.update_status('Success', get_payment.payment_id)
            result = payment_map.get(user_currency)
            return result(payment_data)
        else:
            flash(payment_data['message'])
            PaymentsDB.update_status('Error', get_payment.payment_id)
            app.logger.debug(f'{payment_data.__name__} Response error message: {payment_data["message"]}')
            return render_template('payment.html')
    else:
        return render_template('payment.html')


@app.after_request
def after_request(responce):
    g.db.close()
    return responce


@app.errorhandler(Exception)
def internal_error(exception):
    app.logger.error(exception)
    flash(exception)
    return render_template('payment.html')
