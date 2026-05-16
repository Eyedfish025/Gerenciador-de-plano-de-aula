from flask import Flask
from models import *



app = Flask(__name__)

from views import *

Base.metadata.create_all(bind=dbaula)

if __name__ == "__main__":
    app.run()