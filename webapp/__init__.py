from flask import Flask
from logging.config import fileConfig
import os


fileConfig('logging.conf', disable_existing_loggers=False)

app = Flask(__name__)
app.secret_key = os.urandom(16)

import webapp.urls
