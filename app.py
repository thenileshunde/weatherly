import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'qwertyuiopsecretkey'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


# app.config['DEBUG'] = True

key = 'c9f1f34212b6ce232a81ca55ffc01e4f'
unit = 'metric'
url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid={}'


def get_weather_data(city):
    r = requests.get(url.format(city, unit, key)).json()
    return r


@app.route('/')
def index_get():
    cities = City.query.all()
    
    weather_data = []
    
    
    for city in cities:
        r = get_weather_data(city.name)
        # print(r)
        #
        weather = {
            'city': city.name,
            'temperature': round(r['main']['temp']),
            'description': str(r['weather'][0]['description']).title(),
            'icon': r['weather'][0]['icon'],
            'humidity':r['main']['humidity'],
            'wind': r['wind']['speed']
        }
        
        weather_data.append(weather)
        
        
    
    return render_template('index.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    
    new_city = request.form.get('city').strip().lower()
    
    res = get_weather_data(new_city)
    
    if res['cod'] == 200 and new_city:
        
        city_exists = City.query.filter(City.name.ilike(f"%{new_city}%")).first()
        
        if not city_exists:
            
            city_to_add = City(name=new_city.title())
            db.session.add(city_to_add)
            db.session.commit()
        else:
            err_msg = 'City Already Exists'
    else:
        err_msg = 'City does not exist in the world !'
    
    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City Added Successfully !', 'success')
    
    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    
    flash('Successfully Deleted {}'.format(city.name),'success')
    
    return redirect(url_for('index_get'))


if __name__ == "__main__":
    app.run(debug=True)
