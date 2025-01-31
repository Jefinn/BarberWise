from flask import Flask
app = Flask(__name__)
from app import routes
import os

app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória