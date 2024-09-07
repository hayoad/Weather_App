import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "it'saSecret"
db = SQLAlchemy(app)

class City(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
 
def get_weather_data(city):
     url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=f9b2bca7c67ad106ad8d01a616759ad2'
     r = requests.get(url).json()
     return r


@app.route('/') 
def index_get():
    if request.method == 'POST':
        new_city = request.form.get('city')
        
        if new_city:
            new_city_obj = City(name=new_city)  # type: ignore

            db.session.add(new_city_obj)
            db.session.commit()
    cities = City.query.all()
 
    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        print(r)

        weather = {
             'city' : city.name,
             'temperature' :  r['main']['temp'],
             'description' : r['weather'][0]['description'], 
             'icon' : r['weather'][0]['icon'],
         }
         
        weather_data.append(weather)
    

    return render_template('weather.html', weather_data=weather_data)




@app.route('/', methods=['POST']) 
def index_post():
     err_msg = ''
     new_city = request.form.get('city')

     if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)  # type: ignore

                db.session.add(new_city_obj)
                db.session.commit()

            else:
                err_msg = 'City does not exist in the world!'

        else:
            err_msg = 'City already exists in the database!'
    
     if err_msg:
         flash(err_msg, 'error')
     else:
         flash('City added successfully!')

     return redirect(url_for('index_get'))
    

@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted { city.name }', 'success' )
    return redirect(url_for('index_get'))