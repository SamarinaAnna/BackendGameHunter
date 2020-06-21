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
    login = None
    pas = None
    if request.method == 'POST':
        k = gameHunter.inputUser(request.form['username'], request.form['password'])
        d = {'dict': 1, 'dictionary': 2}
        data = {'login': request.form['username'], 'pas': request.form['password']}
        login = request.form['username']
        pas = request.form['password']
        if k:
            session['logged_in'] = True
            #flash('You were logged in')
            g.user = k
            global user_string
            user_string = k
            #print(user_string)
            return redirect(url_for('get_person'))
        else: error = 'Неправильный логин или пароль!'
    return render_template('login.html', error=error, login = login, pas = pas)


@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    name_emp = name
    surname_emp = surname
    email_emp = email
    password_emp = password

    if request.method == 'POST':
        if not (password or password2):
            flash('Пожалуйста, заполните все поля!')
        elif not name or not surname or not email:
            flash('Пожалуйста, заполните все поля!')
        elif (len(name_emp.replace(" ", "")) == 0 or len(surname_emp.replace(" ", "")) == 0 or len(email_emp.replace(" ", "")) == 0 or len(password_emp.replace(" ", "")) == 0):
            flash('Пожалуйста, заполните все поля!')
        elif (gameHunter.coll.find_one({"email": str(email)}, {"email": 1, "_id": 0})):
            flash('Такой email уже существует!')
        elif(len(password) < 3):
            flash('Пароль должен содержать не менее 3-х символов')
        elif password != password2:
            flash('Пароль не совпадает!')
        else:
            gameHunter.registrationUser(str(name), str(surname), str(phone), str(email), password)

            k = gameHunter.inputUser(str(email), password)
            if k:
                session['logged_in'] = True
                #flash('You were logged in')
                g.user = k
                global user_string
                user_string = k

            return redirect(url_for('get_person'))

    return render_template('register.html', name=name, surname=surname, phone=phone, email=email, password=password, password2=password2)


#профиль пользователя
@app.route('/get_person', methods=['GET'])
def get_person():
    global user_string
    if user_string != "":
        return render_template('get_person.html', user=user_string)
    else:
        return render_template('login.html')


#объявления конкретного пользователя (залогиневшегося)
@app.route('/my_ad', methods=['GET'])
def my_ad():
    global user_string
    if user_string != "":
        t = gameHunter.SpecificUserAds(gameHunter.coll.find_one({"_id": user_string['_id']}, {"_id": 1}))
        return render_template('my_ad.html', messages=t)
    else:
        return render_template('login.html')


#страница с формами для добавления объявления
@app.route('/form_for_add_ad', methods=['GET', 'POST'])
def form_for_add_ad():
    global user_string
    if user_string != "":
        return render_template('form_for_add_ad.html')
    else:
        return render_template('login.html')


#страница с объявлениями
@app.route('/all_ad', methods=['GET'])
def all_ad():
    global user_string
    if user_string != "":
        u = gameHunter.AdsDateSort()
        for_status = user_string
        return render_template('all_ad.html', messages=u, for_status=for_status)
    else:
        return render_template('login.html')


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
    #flash('You were logged out')
    #g.user = None
    global user_string
    user_string = ""
    return redirect(url_for('index'))




#обработка полученного объявления (нет html)///////////////////////////////////////////////////////////////////////////////////////
@app.route('/add_message', methods=['POST'])
def add_message():
    global user_string
    error = None
    if user_string != "":

        date = str(request.form['date'])
        time = str(request.form['time'])
        place = str(request.form['place'])
        quantityPlayers = request.form['quantity']
        nameGame = str(request.form['game_name'])
        duration = str(request.form['duration'])
        description = str(request.form['description'])
        recordedPlayers = []

        date_emp = date
        time_emp = time
        place_emp = place
        nameGame_emp = nameGame
        duration_emp = duration

        if request.method == 'POST':
            if not date or not time or not place or not duration or not quantityPlayers or not nameGame:
                error = 'Пожалуйста, заполните все поля!'
            elif (len(date_emp.replace(" ", "")) == 0 or len(time_emp.replace(" ", "")) == 0 or len(place_emp.replace(" ", "")) == 0 or len(nameGame_emp.replace(" ", "")) == 0 or len(duration_emp.replace(" ", "")) == 0):
                error = 'Пожалуйста, заполните все поля!'
            else:
                gameHunter.createAd(str(user_string['_id']), str(date), str(time), str(place), int(quantityPlayers),
                                    str(nameGame), str(duration), str(description), recordedPlayers)

                return redirect(url_for('my_ad'))

        return render_template('form_for_add_ad.html', error=error, date = request.form['date'], 
        time = request.form['time'], place = request.form['place'], quantityPlayers = request.form['quantity'], 
        nameGame = request.form['game_name'], duration = request.form['duration'], description = request.form['description'])
    else:
        return redirect(url_for('login'))


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
    global user_string, temp
    if user_string != "":

        idAd = gameHunter.coll1.find_one({"_id": ObjectId(ad_id)}, {"_id": 1})
        idUser = gameHunter.coll.find_one({"_id": ObjectId(user_string['_id'])}, {"_id": 1})

        u = gameHunter.AdsDateSort()
        for i in u:
            if i['_id'] == ObjectId(ad_id):
                temp = i

        if temp['dataCreator']['_id'] != idUser['_id']:
            gameHunter.RecordingAnAd(idAd, idUser)

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
