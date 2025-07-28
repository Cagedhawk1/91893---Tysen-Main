import os
from flask import Flask
from models import db  # import db, SQLAlchemy, and models
from routes import register_routes  # function that registers Flask routes
from flask_bootstrap import Bootstrap


# Create the app at module level
app = Flask(__name__, instance_relative_config=True)
Bootstrap(app)

# check if instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# database path (in the instance folder)
DB_FILENAME = 'database.db'
DB_PATH = os.path.join(app.instance_path, DB_FILENAME)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize plugins
db.init_app(app)

# CREATE DB ONLY IF IT DOES 
with app.app_context():
    if not os.path.exists(DB_PATH):
        db.create_all()

# Register routes
register_routes(app, db)

# Optional: Keep create_app() for flexibility
def create_app():
    """Generate Docstring | X
    Create the app.
    """
    # This can be used for testing or different configs
    new_app = Flask(__name__, instance_relative_config=True)
    new_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    new_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(new_app)
    with new_app.app_context():
        if not os.path.exists(DB_PATH):
            db.create_all()
    register_routes(new_app, db)
    return new_app

if __name__ == "__main__":
    # create the app again?
    app = create_app()
    app.run(debug=True)