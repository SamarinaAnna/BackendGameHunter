from collections import namedtuple

from werkzeug.security import generate_password_hash

import gameHunter
from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, make_response, session, flash, g
from flask_restful import Api, Resource, reqparse
from flask_login import login_user, logout_user, current_user, login_required
from bson.objectid import ObjectId



app = Flask(__name__)

user_string = ""
#///////////////////////////////////////////////////////
app.config.from_object(__name__)



# Загружаем конфиг по умолчанию и переопределяем в конфигурации часть
# значений через переменную окружения
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)
#///////////////////////////////////////////////////////////////

api = Api(app)

#вход///////////////////////////////////////////////////////////////////////////
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        k = gameHunter.inputUser(request.form['username'], request.form['password'])
        if k:
            session['logged_in'] = True
            flash('You were logged in')
            g.user = k
            global user_string
            user_string = k
            return redirect(url_for('index'))
        else: error = 'Invalid username or password'
    return render_template('login.html', error=error)
#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    error = None
#    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
#            session['logged_in'] = True
#            flash('You were logged in')
#            return redirect(url_for('main'))
#    return render_template('login.html', error=error)

#выход

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    #g.user = None
    global user_string
    user_string = ""
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (name or surname or email or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            gameHunter.registrationUser(str(name), str(surname), str(phone), str(email), password)

            return redirect(url_for('login'))

    return render_template('register.html')


#первая страница + список объявлений (аргументы не нужны)
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    u = gameHunter.AdsDateSort()
    return render_template('index.html', messages=u)

#страница с формами для добавления объявления
@app.route('/main', methods=['GET'])
def form_for_add_ad():
    u = gameHunter.AdsDateSort()
    return render_template('main.html', messages=u)

#объявления конкретного пользователя (залогиневшегося)
@app.route('/my_ad', methods=['GET'])
def my_ad():
    global user_string
    t = gameHunter.SpecificUserAds(gameHunter.coll.find_one({"_id": user_string['_id']}, {"_id": 1}))
    return render_template('my_ad.html', messages=t)

#обработка полученного объявления
@app.route('/add_message', methods=['POST'])
def add_message():
    global user_string
    if user_string != "":
        date = request.form['date']
        time = request.form['time']
        place = request.form['place']
        quantityPlayers = request.form['quantity']
        nameGame = request.form['game_name']
        duration = request.form['duration']
        description = request.form['description']
        recordedPlayers = []

        gameHunter.createAd(str(user_string['_id']), str(date), str(time), str(place), int(quantityPlayers), str(nameGame), str(duration), str(description), recordedPlayers)

        u = gameHunter.AdsDateSort()

        return render_template('index.html', messages=u)
    else: return render_template('login.html')

#страница с формами для удаления объявления
@app.route('/form_for_del', methods=['GET'])
def form_for_dell_ad():
    u = gameHunter.AdsDateSort()
    return render_template('form_for_del.html', messages=u)

#обработка полученного объявления
@app.route('/del_message', methods=['POST'])
def del_message():
    global user_string
    if user_string != "":
        date = request.form['date']
        time = request.form['time']
        place = request.form['place']
        quantityPlayers = request.form['quantity']
        nameGame = request.form['game_name']
        duration = request.form['duration']

        gameHunter.DeleteAd(user_string, str(date), str(time), str(place), int(quantityPlayers), str(nameGame), str(duration))

        u = gameHunter.AdsDateSort()

        return render_template('index.html', messages=u)
    else: return render_template('login.html')

#запись на игру
@app.route('/add_player/<ad_id>')
def add_player(ad_id):
    global user_string
    if user_string != "":
        idAd = gameHunter.coll1.find_one({"_id": ObjectId(ad_id)}, {"_id": 1})
        idUser = gameHunter.coll.find_one({"_id": ObjectId(user_string['_id'])}, {"_id": 1})

        gameHunter.RecordingAnAd(idAd, idUser)

        u = gameHunter.AdsDateSort()

        return render_template('index.html', messages=u)
    else: return render_template('login.html')

#отписаться от игры
@app.route('/dell_player/<ad_id>')
def dell_player(ad_id):
    global user_string
    if user_string != "":
        idAd1 = gameHunter.coll1.find_one({"_id": ObjectId(ad_id)}, {"_id": 1})
        idUser1 = gameHunter.coll.find_one({"_id": ObjectId(user_string['_id'])}, {"_id": 1})

        gameHunter.UnsubscribeFromParticipation(idAd1, idUser1)

        u = gameHunter.AdsDateSort()

        return render_template('index.html', messages=u)
    else: return render_template('login.html')

#при ошибке (теоретически, не нужно, можно удалить)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#список людей (нет ф-ии, использована заглушка)
#@app.route('/get_persons', methods=['GET'])
#def get_persons():
#    return render_template('get_persons.html', gamers=gamers)

#вывод человека по почте (нет ф-ии, использована заглушка)
#@app.route('/get_person/<email>', methods=['GET'])
#def get_person(email):
#   lis_per = []
#    for per in gamers:
#        print(per.email)
#        if per.email == email:
#            lis_per.append(per)
#    return render_template('get_person.html', gamers=lis_per)

app.run()
