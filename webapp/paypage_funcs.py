from flask import render_template, redirect


def pay_page_payment(req):
    return render_template("pay_page.html", result=req)


def bill_payment(req):
    url = req['data']['url']
    return redirect(url)


def invoice_payment(req):
    return render_template("pay_page.html", result=req['data'])


currency_to_func_map = {
    '978': pay_page_payment,
    '840': bill_payment,
    '643': invoice_payment
}
