import os
from flask import Flask
from models import db
from routes import register_routes
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

# Initialize SQLAlchemy
db = SQLAlchemy()
# Initalise bootstrap
bootstrap = Bootstrap()
# Configuring the flask routes 
app = Flask(__name__, static_url_path='/static', static_folder='static')
def create_app():
    # Create the app at module level
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    # Check if instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Database path (in the instance folder)
    DB_FILENAME = 'database.db'
    DB_PATH = os.path.join(app.instance_path, DB_FILENAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize plugins
    db.init_app(app)

    # CREATE DB ONLY IF IT DOES NOT EXIST
    with app.app_context():
        if not os.path.exists(DB_PATH):
            db.create_all()

    # Register routes file
    from routes import register_routes
    register_routes(app, db)

    return app

if __name__ == '__main__':
    # Create the app again?
    app = create_app()
    app.run()