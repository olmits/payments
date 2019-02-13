from flask import render_template, request, redirect, flash, g
from webapp import app
from webapp.payment import Payment
from webapp.db_model import PaymentsDB, db_proxy


@app.before_request
def before_request():
    g.db = db_proxy
    g.db.connect()


@app.route('/')
@app.route('/result', methods=['POST', 'GET'])
def get_output():
    if request.method == 'POST':

        form = request.form
        get_payment = Payment.create_payment(form.get('currency'), form)
        send_request = get_payment.request()

        if not send_request['data'] is None:
            PaymentsDB.update_status('Success', get_payment.payment_id)

            if form['currency'] == '978':
                return render_template("pay_page.html", result=send_request)

            elif form['currency'] == '840':
                url = send_request['data']['url']
                return redirect(url)

            else:
                return render_template("pay_page.html", result=send_request['data'])
        else:
            flash(send_request['message'])
            PaymentsDB.update_status('Error', get_payment.payment_id)
            app.logger.debug(f'{send_request.__name__} Response error message: {send_request["message"]}')
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
