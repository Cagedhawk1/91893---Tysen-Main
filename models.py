from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Initialize the database
db = SQLAlchemy()


# Bodystyle table
class Car_bodystyle(db.Model):
    __tablename__ = 'car_bodystyle'
    bodystyle_id = db.Column(db.Integer, primary_key=True)
    bodystyle_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Car_bodystyle {self.bodystyle_name}>'

# Manufacturer table
class Car_manufacturer(db.Model):
    __tablename__ = 'car_manufacturer'
    manufacturer_id = db.Column(db.Integer, primary_key=True)
    manufacturer_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Car_manufacturer {self.manufacturer_name}>'

# Model table
class Car_model(db.Model):
    __tablename__ = 'car_model'
    model_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    model_horsepower = db.Column(db.Integer)
    model_torque = db.Column(db.Integer)
    eco_rating = db.Column(db.Integer)
    safety_rating = db.Column(db.Integer)
    model_seats = db.Column(db.Integer)

    def __repr__(self):
        return f'<Car_model {self.model_name}>'

# Image table
class car_images(db.Model):
    __tablename__ = 'car_images'
    image_id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String)  
    image_car = db.Column(db.String(100))

    def __repr__(self):
        return f'<car_images {self.image_id}>'

# Stock table
class Car_stock(db.Model):
    __tablename__ = 'car_stock'
    stock_id = db.Column(db.Integer, primary_key=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('car_manufacturer.manufacturer_id'), nullable=False)
    bodystyle_id = db.Column(db.Integer, db.ForeignKey('car_bodystyle.bodystyle_id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('car_model.model_id'), nullable=False)
    year = db.Column(db.Date)
    car_price = db.Column(db.Integer)
    distance = db.Column(db.Integer)
    image_id = db.Column(db.Integer, db.ForeignKey('car_images.image_id'))
    
    # Relationships
    manufacturer = db.relationship('Car_manufacturer', backref='stock_entries')
    bodystyle = db.relationship('Car_bodystyle', backref='stock_entries')
    model = db.relationship('Car_model', backref='stock_entries')
    image = db.relationship('car_images', backref='stock_entries')

# Returning all objects in the database
    def __repr__(self):
        return f'<Car_stock {self.stock_id}>'