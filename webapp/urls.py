from flask import render_template, request, redirect, flash, g
from webapp import app
from webapp.payment import Payment
from webapp.db_model import PaymentsDB, db_proxy


@app.before_request
def before_request():
    g.db = db_proxy
    g.db.connect()


@app.after_request
def after_request(responce):
    g.db.close()
    return responce


@app.route('/')
def initial_form():
    return render_template('payment.html')


@app.route('/result', methods=['POST', 'GET'])
def get_output():
    if request.method == 'POST':
        form = request.form

        get_processor = Payment.get_subclass(form['currency'])
        prepared_data = get_processor.form_processing(form)
        result = prepared_data.request()

        if not result['data'] is None:
            PaymentsDB.update_status('Success', prepared_data.payment_id)
            if form['currency'] == '978':
                return render_template("pay_page.html", result=result)
            elif form['currency'] == '840':
                url = result['data']['url']
                return redirect(url)
            else:
                return render_template("pay_page.html", result=result['data'])
        else:
            flash(result['message'])
            PaymentsDB.update_status('Error', prepared_data.payment_id)
            app.logger.debug(f'{get_processor.__name__} Response error message: {result["message"]}')
            return render_template('payment.html')


@app.errorhandler(Exception)
def internal_error(exception):
    app.logger.error(exception)
    flash(exception)
    return render_template('payment.html')
