import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


# app.config['DEBUG'] = True

@app.route('/', methods=['GET', 'POST'])
def index():
    key = 'c9f1f34212b6ce232a81ca55ffc01e4f'
    unit = 'metric'
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid={}'
    
    not_found_flag = 0
    
    if request.method == 'POST':
        new_city = request.form.get('city').strip()
        
        res = requests.get(url.format(new_city, unit, key)).json()
        
        if res['cod'] == 200 and new_city:
            city_to_add = City(name=new_city)
            db.session.add(city_to_add)
            db.session.commit()
        elif(new_city == ''):
            not_found_flag = 0
        else:
            not_found_flag = 1
    
    cities = City.query.all()
    
    weather_data = []
    
    for city in cities:
        r = requests.get(url.format(city.name, unit, key)).json()
        # print(r)
        #
        weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon']
        }
        
        weather_data.append(weather)
    
    return render_template('index.html', weather_data=weather_data, flag=not_found_flag)


if __name__ == "__main__":
    app.run(debug=True)
