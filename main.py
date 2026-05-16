from flask import Flask
from models import *
from route import *

app = Flask(__name__)

Base.metadata.create_all(bind=dbaula)

if __name__ == "__main__":
    app.run()