import os
import secrets
import requests
from PIL import Image
from weather import app, bcrypt, db
from flask import render_template, request, flash, session, redirect, url_for
from flask_wtf.csrf import CSRFError
from weather.models import City, User
from weather.forms import RegistrationForm, LoginForm, Account_configForm
from weather.tables import LocationTable
from flask_login import login_user, current_user, logout_user, login_required

# Process favicon.ico requests
class icon:
    def GET(self): raise web.seeother("/static/favicon.png")


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


@app.route("/")
@login_required
def index():

	user = User.query.get(current_user.id)
	
	url= 'http://weerlive.nl/api/json-data-10min.php?key=a00ff03d0d&locatie={}'
	
	weather_data = []
	
	for city in user.cities:
	
	    r = requests.get(url.format(city.name)).json()
	
	    weather = {
	        'icon' : r['liveweer'][0]['image'],
	        'city' : city.name,
	        'temperature' : r['liveweer'][0]['temp'],
	        'luchtdruk' : r['liveweer'][0]['luchtd'],
	        'wind_richting': r['liveweer'][0]['windr'],
	        'wind_v': r['liveweer'][0]['windms'],
	        'expected_max_temp' : r['liveweer'][0]['d0tmax'],
	        'expected_min_temp' :r['liveweer'][0]['d0tmin'],
	        'expected_wind_richting': r['liveweer'][0]['d0windr'],
	        'expected_wind_v': r['liveweer'][0]['d0windms'],
	        'expected_icon': r['liveweer'][0]['d0weer'],
	        'description' : r['liveweer'][0]['verw'],
	        'tomorrow_max_temp' : r['liveweer'][0]['d1tmax'],
	        'tomorrow_min_temp' :r['liveweer'][0]['d1tmin'],
	        'tomorrow_wind_richting': r['liveweer'][0]['d1windr'],
	        'tomorrow_wind_v': r['liveweer'][0]['d1windms'],
	        'tomorrow_icon': r['liveweer'][0]['d1weer'],
	        'dayaftertomorrow_max_temp' : r['liveweer'][0]['d2tmax'],
	        'dayaftertomorrow_min_temp' :r['liveweer'][0]['d2tmin'],
	        'dayaftertomorrow_wind_richting': r['liveweer'][0]['d2windr'],
	        'dayaftertomorrow_wind_v': r['liveweer'][0]['d2windms'],
	        'dayaftertomorrow_icon': r['liveweer'][0]['d2weer'],
	    }
	
	    weather_data.append(weather)
	
	r = requests.get('http://weerlive.nl/api/json-data-10min.php?key=a00ff03d0d&locatie=Bilt').json()
	if r['liveweer'][0]['alarm'] != '0':
	    alarm_information = {
	        'alarm': r['liveweer'][0]['alarm'],
	        'alarmtxt': r['liveweer'][0]['alarmtxt'],
	    }
	else:
	    alarm_information = {
	        'alarm': r['liveweer'][0]['alarm'],
	    }
	
	return render_template('weather.html', title='weer info', weather_data=weather_data, alarm_information=alarm_information)


ButtonPressed=0
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', buttonpressed=ButtonPressed)


@app.route("/locations", methods=['GET', 'POST'])
def locations():
    return render_template('locations.html')



def delete_old_profile_picture(old_profile_picture):
	profile_picture_path = os.path.join(app.root_path, 'static/profile_pics', old_profile_picture)
	return os.osremove(iprofile_picture_path, tmp_profile_picture)

	

def save_profile_picture(form_profile_picture):
	garbled_string = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_profile_picture.filename)
	random_profile_picture_name = garbled_string + f_ext
	profile_picture_path = os.path.join(app.root_path, 'static/profile_pics', random_profile_picture_name)
	output_size = (125, 125)
	img = Image.open(form_profile_picture)
	img.thumbnail(output_size)
	img.save(profile_picture_path)
	return random_profile_picture_name



@app.route("/account_config", methods=['GET', 'POST'])
@login_required
def account():
    form = Account_configForm()
    tmp_profile_picture = form.profile_picture
    if form.validate_on_submit():
        if form.profile_picture.data:
            profile_picture_file = save_profile_picture(form.profile_picture.data)
            current_user.image_file = profile_picture_file
        current_user.user_name = form.user_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Jouw account is bijgewerkt', 'is-success')
        return redirect(url_for('account'))
    else:
        if request.method == 'GET':
            form.user_name.data = current_user.user_name
            form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    user = User.query.get(current_user.id)
    Locations = user.cities
    LocationTable.border = True
    return render_template('account_config.html', title='Gebruiker config', image_file=image_file, Locations=Locations, form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
	    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
	    user = User(user_name=form.user_name.data, email=form.email.data, password=hashed_password)
	    db.session.add(user)
	    db.session.commit()
	    flash('Gebruiker is geregistreerd', 'is-success')
	    return redirect(url_for('login'))
	return render_template('register.html', title='registreer', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('index'))
		else:
			flash('Aanmelden is mislukt! Controleer het email address en password')
	return render_template('login.html', title='aanmelden', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

