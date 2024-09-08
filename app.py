import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Flask App Configuration
app = Flask(__name__)
app.config['DEBUG'] = True  # Enable debug mode for development (remove in production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'  # Local SQLite database path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable unnecessary tracking
app.config['SECRET_KEY'] = "it'saSecret"  # Secret key for session management (replace with a strong value)

# Initialize SQLAlchemy Database Object
db = SQLAlchemy(app)

# City Model Definition
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each city
    name = db.Column(db.String(50), nullable=False)  # City name (non-nullable)

# Function to Fetch Weather Data from OpenWeatherMap API
def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=f9b2bca7c67ad106ad8d01a616759ad2'
    r = requests.get(url).json()
    return r  # Return the JSON response

# Route for the Main Weather Page (GET Method)
@app.route('/')
def index_get():
    if request.method == 'POST':
        return redirect(url_for('index_post'))  # Handle POST requests in a dedicated route

    cities = City.query.all()  # Fetch all cities from the database

    weather_data = []
    for city in cities:
        # Fetch and process weather data for each city
        r = get_weather_data(city.name)
        weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }
        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)

# Route for Adding a City (POST Method)
@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            # Check API response code for valid city
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)  # Create a new City object
                db.session.add(new_city_obj)
                db.session.commit()
                flash('City added successfully!', 'success')  # Flash success message
            else:
                err_msg = 'City not found on OpenWeatherMap!'
        else:
            err_msg = 'City already exists in your database!'

    if err_msg:
        flash(err_msg, 'error')  # Flash error message

    return redirect(url_for('index_get'))  # Redirect back to the main page

# Route for Deleting a City
@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    if city:
        db.session.delete(city)
        db.session.commit()
        flash(f'Successfully deleted {city.name}', 'success')
    else:
        flash(f'City "{name}" not found!', 'error')

    return redirect(url_for('index_get'))

# (Optional) Add routes for editing city information as needed