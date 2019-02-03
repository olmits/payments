# Piastrix payments WEB Api

## Pre-requisites
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Install [Heroku Postgress](https://devcenter.heroku.com/articles/heroku-postgresql#pg-psql)
## Getting Started
### Deploying the app
1. Clone repository:
```
$ git clone https://github.com/olmits/payments.git
$ cd payments
```
2. Deploy app on Heroku:
```
$ heroku create
$ git push heroku master
```
### Setting up a new database
1. Create a new database on Heroku as an add-on:
```
$ heroku addons:create heroku-postgresql:<name>
```
2. Set up a config variable:
```
$ heroku config:set HEROKU=1
```
3. For creating new table on datebase, launch a shell on Heroku and run:
```
$ python db_model.py
```

### Setting up logging add-on
1. Add [Billing information](https://devcenter.heroku.com/articles/account-verification)
2. Install Timder.io logging add-on:
```
$ heroku addons:create timber-logging:free
```
