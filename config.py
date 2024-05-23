import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://myuser:mypassword@localhost/my_flask_app_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False