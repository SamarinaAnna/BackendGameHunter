import gameHunter
from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response, session, flash, g
from flask_restful import Api
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
#///////////////////////////////////////////////////////////////

api = Api(app)


#первая страница "о нас"
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


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
            #print(user_string)
            return redirect(url_for('get_person'))
        else: error = 'Invalid username or password'
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    print(name)

    if request.method == 'POST':
        if not (password or password2):
            flash('Please, fill all fields!')
        elif not name or not surname or not email:
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            gameHunter.registrationUser(str(name), str(surname), str(phone), str(email), password)

            k = gameHunter.inputUser(str(email), password)
            if k:
                session['logged_in'] = True
                flash('You were logged in')
                g.user = k
                global user_string
                user_string = k

            return redirect(url_for('get_person'))

    return render_template('register.html')

#профиль пользователя
@app.route('/get_person', methods=['GET'])
def get_person():
    return render_template('get_person.html', user=user_string)


#объявления конкретного пользователя (залогиневшегося)
@app.route('/my_ad', methods=['GET'])
def my_ad():
    global user_string
    t = gameHunter.SpecificUserAds(gameHunter.coll.find_one({"_id": user_string['_id']}, {"_id": 1}))
    return render_template('my_ad.html', messages=t)


#страница с формами для добавления объявления
@app.route('/form_for_add_ad', methods=['GET'])
def form_for_add_ad():
    return render_template('form_for_add_ad.html')


#страница с объявлениями
@app.route('/all_ad', methods=['GET'])
def all_ad():
    u = gameHunter.AdsDateSort()
    return render_template('all_ad.html', messages=u)

#страница с объявлениями, на которые записан пользователь
@app.route('/all_ad_on_record', methods=['GET'])
def all_ad_on_record():
    global user_string
    if user_string != "":
        u = gameHunter.AdsDateSort()
        temp = []
        for i in u:
            for j in i['recordedPlayers']:
                if j['_id'] == user_string['_id']:
                    temp.append(i)

        return render_template('all_ad_on_record.html', messages=temp)
    else:
        return render_template('login.html')


#выход
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    #g.user = None
    global user_string
    user_string = ""
    return redirect(url_for('index'))




#обработка полученного объявления (нет html)
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

        return redirect(url_for('my_ad'))
    else: return redirect(url_for('login'))



#обработка удаления объявления (нет html)
@app.route('/del_message/<ad_id>')
def del_message(ad_id):
    global user_string, temp
    if user_string != "":
        u = gameHunter.AdsDateSort()
        for i in u:
            if i['_id'] == ObjectId(ad_id):
                temp = i
        date = str(temp['date'])
        time = str(temp['time'])
        place = str(temp['place'])
        quantityPlayers = int(temp['quantityPlayers'])
        nameGame = str(temp['nameGame'])
        duration = str(temp['duration'])

        gameHunter.DeleteAd(user_string, date, time, place, quantityPlayers, nameGame, duration)

        return redirect(url_for('my_ad'))
    else: return render_template('login.html')

#запись на игру (нет html)
@app.route('/add_player/<ad_id>')
def add_player(ad_id):
    global user_string
    if user_string != "":
        idAd = gameHunter.coll1.find_one({"_id": ObjectId(ad_id)}, {"_id": 1})
        idUser = gameHunter.coll.find_one({"_id": ObjectId(user_string['_id'])}, {"_id": 1})

        gameHunter.RecordingAnAd(idAd, idUser)

        #u = gameHunter.AdsDateSort()

        #return render_template('all_ad.html', messages=u)

        return redirect(url_for('all_ad'))
    else: return render_template('login.html')

#отписаться от игры (нет html)
@app.route('/dell_player/<ad_id>')
def dell_player(ad_id):
    global user_string
    if user_string != "":
        idAd1 = gameHunter.coll1.find_one({"_id": ObjectId(ad_id)}, {"_id": 1})
        idUser1 = gameHunter.coll.find_one({"_id": ObjectId(user_string['_id'])}, {"_id": 1})

        gameHunter.UnsubscribeFromParticipation(idAd1, idUser1)

        return redirect(url_for('all_ad'))
    else: return render_template('login.html')

#при ошибке (теоретически, не нужно, можно удалить)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


app.run()
