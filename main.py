import os
from dotenv import load_dotenv
from flask import Flask
from models import *

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

from views import *

Base.metadata.create_all(bind=dbaula)

if __name__ == "__main__":
    app.run()