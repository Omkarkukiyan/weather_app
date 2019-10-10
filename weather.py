import requests
from flask import Flask
from flask import render_template ,request,redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'

db= SQLAlchemy(app)

class City(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(60), nullable=False)


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=6fef4e94c731959df953596baefc1240'
    r = requests.get(url.format(url)).json()
    return r

@app.route('/')
def index_get():

    cities= City.query.all()
    weather_data=[]
    for city in cities:
        r=get_weather_data(city.name)
        print(r)

        weather = {
            'city':city.name,
            'temperature' :r['main']['temp'],
            'description':r['weather'][0]['description'],
            'icon':r['weather'][0]['icon']
        }
        weather_data.append(weather)
    return render_template('weather.html', weather_data=weather_data)



@app.route('/', methods=['POST'])
def index_post():
    error_msg=''
    new_city = request.form.get('city')
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data= get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                error_msg='City does not exist in the world'
        else:
            error_msg='City already exists!'

    if error_msg:
        flash(error_msg, 'error')
    else:
        flash('City added sucessfully')
    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city=City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'Successfully deleted { city.name }', 'success')
    return redirect(url_for('index_get'))