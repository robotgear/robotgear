from flask import Flask
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore
from database import db_session, init_db
from models import User, Role
import config


# Create app
app = Flask(__name__)
app.config.from_object(config.ProductionConfig)

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    init_db()
    user_datastore.create_user(email='bkeeneykid@me.com', password='password')
    db_session.commit()

# Views
@app.route('/')
def home():
    print("test")
    return 'Here you go!'

if __name__ == '__main__':
    app.run()