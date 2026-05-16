import os

from dotenv import load_dotenv
from flask import Flask

import models
import views

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")


models.Base.metadata.create_all(bind=models.dbaula)

if __name__ == "__main__":
    views.app.run()
