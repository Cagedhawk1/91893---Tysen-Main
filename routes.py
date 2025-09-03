from models import Car_manufacturer, Car_bodystyle, Car_model, Car_stock, car_images
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, send_file, abort
import sqlite3
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import *
from io import BytesIO

# Registering routes to the app
def register_routes(app, db):

    # Creates contents page
    @app.route('/contents')
    def contents():
        query = request.args.get('query', '')
        # Joins to get all cars with their related information into the table
        cars = db.session.query(Car_stock) \
            .join(Car_manufacturer) \
            .join(Car_bodystyle) \
            .join(Car_model) \
            .join(car_images) \
            .options(
                joinedload(Car_stock.manufacturer),
                joinedload(Car_stock.bodystyle),
                joinedload(Car_stock.model),
                joinedload(Car_stock.image)
            )

        # Filter on manufacturer or model name
        if query:
            cars = cars.filter(
                (Car_manufacturer.manufacturer_name.like(f'%{query}%')) |
                (Car_model.model_name.like(f'%{query}%'))
            )
        
        cars = cars.all()
        return render_template('contents.html', cars=cars)

    # Gets image from the database 
    @app.route('/images/<int:image_id>')
    def serve_image(image_id):
        img = db.session.get(car_images, image_id)
        if not img or not img.image:
            abort(404)
        return send_file(BytesIO(img.image), mimetype='image/jpeg')
    
    # Legacy home page
    @app.route('/Legacyhome')
    def legacyhome():
        return render_template('Legacyhome.html')

    # Creates Main home page 
    @app.route('/')
    def devhome():
        # Loads carousel images and text into the home page
        carousel_items = [
            {
                'image': 'https://www-asia.nissan-cdn.net/content/dam/Nissan/AU/Images/homepage/redesign/compressed/award-NIS4334_Qashqai_2022_homepage_d-with-GDA-2-2000x821.jpg.ximg.full.hero.jpg', 
                'caption': 'New Nissan Qashqai', 
                'subtitle': 'Runout Sale.'
            },
            {
                'image': 'https://www-asia.nissan-cdn.net/content/dam/Nissan/AU/Images/homepage/new-navara-pro-4x-homepage-banner-3840x1574.jpg.ximg.full.hero.jpg', 
                'caption': 'Unbeatable Nissan Navara', 
                'subtitle': 'Unstoppable Deal.'
            },
            {
                'image': 'https://www-asia.nissan-cdn.net/content/dam/Nissan/new-zealand/images/homepage/NIS5140-13_Nissan-X-TRAIL-Production_Digital_HeroDesktop_1620x1152-v.jpg.ximg.full.hero.jpg', 
                'caption': 'Innovative E-Power technology', 
                'subtitle': 'Factory Bonus Offers.'
            },
        ]
        return render_template('home.html', carousel_items=carousel_items)   

    # Creates the add listing page
    @app.route('/add-listing', methods=['GET', 'POST'])
    def add_listing():
        # Render the form to add a new car listing
        if request.method == 'POST':
            try:
                manufacturer_name = request.form['manufacturer']
                bodystyle_name = request.form['bodystyle']
                car_name = request.form['car_name']
                horsepower = int(request.form['horsepower'])
                torque = int(request.form['torque'])
                eco_rating = int(request.form['eco_rating'])
                safety_rating = int(request.form['safety_rating'])
                seats = int(request.form['seats'])
                year = datetime.strptime(request.form['year'], "%Y").date()  
                price = float(request.form['price'])
                distance = int(request.form['distance'])
                
                # Handle image upload safely
                image_file = request.files.get('image')
                if image_file and image_file.filename != '':
                    image_data = image_file.read()
                else:
                    image_data = b''  # Default empty bytes if no image

                # Check if manufacturer already exists
                manufacturer = Car_manufacturer.query.filter_by(manufacturer_name=manufacturer_name).first()
                if not manufacturer:
                    manufacturer = Car_manufacturer(manufacturer_name=manufacturer_name)
                    db.session.add(manufacturer)
                    db.session.commit()

                # Check if bodystyle already exists
                bodystyle = Car_bodystyle.query.filter_by(bodystyle_name=bodystyle_name).first()
                if not bodystyle:
                    bodystyle = Car_bodystyle(bodystyle_name=bodystyle_name)
                    db.session.add(bodystyle)
                    db.session.commit()

                # Create model, image, and stock
                model = Car_model(
                    model_name=car_name,
                    model_horsepower=horsepower,
                    model_torque=torque,
                    eco_rating=eco_rating,
                    safety_rating=safety_rating,
                    model_seats=seats
                )
                
                image = car_images(image=image_data, image_car=f"{car_name}_{year.year}")
                
                # Add model and image first to get their IDs
                db.session.add_all([model, image])
                db.session.commit()
                
                stock = Car_stock(
                    manufacturer=manufacturer,
                    bodystyle=bodystyle,
                    model=model,
                    year=year,
                    car_price=price,
                    distance=distance,
                    image=image
                )

                # Add stock and commit
                db.session.add(stock)
                db.session.commit()

                # Redirect to contents page after adding
                return redirect('/contents')
                
            except Exception as e:
                db.session.rollback()
                return f"Error adding listing: {str(e)}", 500

        return render_template("add-listing.html")

    # Dev command for testing database
    @app.route('/add-sample')
    def add_sample():
        try:
            # Check if manufacturer already exists
            manufacturer = Car_manufacturer.query.filter_by(manufacturer_name="Toyota").first()
            if not manufacturer:
                manufacturer = Car_manufacturer(manufacturer_name="Toyota")
                db.session.add(manufacturer)
                db.session.commit()

            # Check if bodystyle already exists
            bodystyle = Car_bodystyle.query.filter_by(bodystyle_name="Sedan").first()
            if not bodystyle:
                bodystyle = Car_bodystyle(bodystyle_name="Sedan")
                db.session.add(bodystyle)
                db.session.commit()

            model = Car_model(
                model_name="Camry",
                model_horsepower=200,
                model_torque=180,
                eco_rating=8,
                safety_rating=9,
                model_seats=5
            )
            image = car_images(image=b"sample_image_data", image_car="Camry_2020")
            
            db.session.add_all([model, image])
            db.session.commit()
            
            stock = Car_stock(
                manufacturer=manufacturer,
                bodystyle=bodystyle,
                model=model,
                year=datetime.strptime("2020-01-01", "%Y-%m-%d").date(),
                car_price=25000,
                distance=5000,
                image=image
            )
            db.session.add(stock)
            db.session.commit()
            return "Sample data added! <br><a href='/contents'>View contents</a> <br><a href='/'>Back to home</a>"
            
        except Exception as e:
            db.session.rollback()
            return f"Error adding sample data: {str(e)}", 500
    
    # Dev command for testing database - adds 10 cars
    @app.route('/add-10-cars')
    def add_10_cars():
        try:
            # Check if manufacturers already exist
            toyota = Car_manufacturer.query.filter_by(manufacturer_name="Toyota").first()
            if not toyota:
                toyota = Car_manufacturer(manufacturer_name="Toyota")
                db.session.add(toyota)

            honda = Car_manufacturer.query.filter_by(manufacturer_name="Honda").first()
            if not honda:
                honda = Car_manufacturer(manufacturer_name="Honda")
                db.session.add(honda)

            ford = Car_manufacturer.query.filter_by(manufacturer_name="Ford").first()
            if not ford:
                ford = Car_manufacturer(manufacturer_name="Ford")
                db.session.add(ford)

            # Check if bodystyles already exist
            sedan = Car_bodystyle.query.filter_by(bodystyle_name="Sedan").first()
            if not sedan:
                sedan = Car_bodystyle(bodystyle_name="Sedan")
                db.session.add(sedan)

            suv = Car_bodystyle.query.filter_by(bodystyle_name="SUV").first()
            if not suv:
                suv = Car_bodystyle(bodystyle_name="SUV")
                db.session.add(suv)

            hatchback = Car_bodystyle.query.filter_by(bodystyle_name="Hatchback").first()
            if not hatchback:
                hatchback = Car_bodystyle(bodystyle_name="Hatchback")
                db.session.add(hatchback)

            # Commit manufacturers and bodystyles first
            db.session.commit()
            
            # Create 10 cars 
            cars_data = [
                # Toyota Cars
                {
                    "model_name": "Corolla",
                    "horsepower": 140,
                    "torque": 126,
                    "eco_rating": 9,
                    "safety_rating": 8,
                    "seats": 5,
                    "manufacturer": toyota,
                    "bodystyle": sedan,
                    "year": datetime.strptime("2021-03-15", "%Y-%m-%d").date(),
                    "price": 22000,
                    "distance": 15000,
                    "image_name": "Corolla_2021"
                },
                {
                    "model_name": "RAV4",
                    "horsepower": 203,
                    "torque": 184,
                    "eco_rating": 7,
                    "safety_rating": 9,
                    "seats": 5,
                    "manufacturer": toyota,
                    "bodystyle": suv,
                    "year": datetime.strptime("2021-06-10", "%Y-%m-%d").date(),
                    "price": 28000,
                    "distance": 12000,
                    "image_name": "RAV4_2021"
                },
                {
                    "model_name": "Prius",
                    "horsepower": 121,
                    "torque": 105,
                    "eco_rating": 10,
                    "safety_rating": 8,
                    "seats": 5,
                    "manufacturer": toyota,
                    "bodystyle": hatchback,
                    "year": datetime.strptime("2022-01-20", "%Y-%m-%d").date(),
                    "price": 26000,
                    "distance": 8000,
                    "image_name": "Prius_2022"
                },
                # Honda Cars
                {
                    "model_name": "Civic",
                    "horsepower": 158,
                    "torque": 138,
                    "eco_rating": 8,
                    "safety_rating": 9,
                    "seats": 5,
                    "manufacturer": honda,
                    "bodystyle": sedan,
                    "year": datetime.strptime("2022-04-25", "%Y-%m-%d").date(),
                    "price": 23000,
                    "distance": 10000,
                    "image_name": "Civic_2022"
                },
                {
                    "model_name": "CR-V",
                    "horsepower": 190,
                    "torque": 179,
                    "eco_rating": 7,
                    "safety_rating": 9,
                    "seats": 5,
                    "manufacturer": honda,
                    "bodystyle": suv,
                    "year": datetime.strptime("2021-08-12", "%Y-%m-%d").date(),
                    "price": 27000,
                    "distance": 18000,
                    "image_name": "CRV_2021"
                },
                {
                    "model_name": "Accord",
                    "horsepower": 192,
                    "torque": 192,
                    "eco_rating": 8,
                    "safety_rating": 9,
                    "seats": 5,
                    "manufacturer": honda,
                    "bodystyle": sedan,
                    "year": datetime.strptime("2020-11-30", "%Y-%m-%d").date(),
                    "price": 24500,
                    "distance": 22000,
                    "image_name": "Accord_2020"
                },
                {
                    "model_name": "Fit",
                    "horsepower": 130,
                    "torque": 114,
                    "eco_rating": 9,
                    "safety_rating": 7,
                    "seats": 5,
                    "manufacturer": honda,
                    "bodystyle": hatchback,
                    "year": datetime.strptime("2021-02-14", "%Y-%m-%d").date(),
                    "price": 18000,
                    "distance": 25000,
                    "image_name": "Fit_2021"
                },
                # Ford Cars
                {
                    "model_name": "Mustang",
                    "horsepower": 310,
                    "torque": 350,
                    "eco_rating": 5,
                    "safety_rating": 7,
                    "seats": 4,
                    "manufacturer": ford,
                    "bodystyle": sedan,
                    "year": datetime.strptime("2021-05-18", "%Y-%m-%d").date(),
                    "price": 35000,
                    "distance": 8500,
                    "image_name": "Mustang_2021"
                },
                {
                    "model_name": "Explorer",
                    "horsepower": 300,
                    "torque": 310,
                    "eco_rating": 6,
                    "safety_rating": 8,
                    "seats": 7,
                    "manufacturer": ford,
                    "bodystyle": suv,
                    "year": datetime.strptime("2020-09-22", "%Y-%m-%d").date(),
                    "price": 32000,
                    "distance": 30000,
                    "image_name": "Explorer_2020"
                },
                {
                    "model_name": "Focus",
                    "horsepower": 160,
                    "torque": 146,
                    "eco_rating": 8,
                    "safety_rating": 8,
                    "seats": 5,
                    "manufacturer": ford,
                    "bodystyle": hatchback,
                    "year": datetime.strptime("2021-12-05", "%Y-%m-%d").date(),
                    "price": 20000,
                    "distance": 15500,
                    "image_name": "Focus_2021"
                }
            ]

            # Add all cars to the database
            for car_data in cars_data:
                # Create model
                model = Car_model(
                    model_name=car_data["model_name"],
                    model_horsepower=car_data["horsepower"],
                    model_torque=car_data["torque"],
                    eco_rating=car_data["eco_rating"],
                    safety_rating=car_data["safety_rating"],
                    model_seats=car_data["seats"]
                )
                
                # Create image with sample data
                image = car_images(
                    image=f"{car_data['image_name']}.jpg".encode('utf-8'),
                    image_car=car_data["image_name"]
                )
                
                # Add model and image to session
                db.session.add(model)
                db.session.add(image)
                db.session.commit()  # Commit to get IDs for foreign keys
                
                # Create stock entry
                stock = Car_stock(
                    manufacturer=car_data["manufacturer"],
                    bodystyle=car_data["bodystyle"],
                    model=model,
                    year=car_data["year"],
                    car_price=car_data["price"],
                    distance=car_data["distance"],
                    image=image
                )
                
                db.session.add(stock)

            db.session.commit()
            return "10 sample cars added successfully! <br><a href='/contents'>View contents</a> <br><a href='/'>Back to home</a>"
            
        except Exception as e:
            db.session.rollback()
            return f"Error adding 10 cars: {str(e)}", 500