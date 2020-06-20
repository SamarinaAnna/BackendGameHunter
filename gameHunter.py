import pymongo
import uuid
import hashlib
import re
#import string
import json
from bson.objectid import ObjectId
from pymongo import MongoClient

conn = MongoClient(
    "mongodb+srv://anna:.ZVpBF5N!594yUw@cluster0-4tx63.gcp.mongodb.net/gameHunter?retryWrites=true&w=majority")
db = conn["gameHunter"]
coll = db["users"]
coll1 = db["ads"]


def hash_password(password):
    # uuid используется для генерации случайного числа
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = str(hashed_password['password']).split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


def inputUser(email, password):
    emailCheck = coll.find_one({"email": email}, {"email": 1, "_id": 0})
    if (emailCheck):
        hashed_password = (coll.find_one({"email": email}, {"password": 1, "_id": 0}))
        if (check_password(hashed_password, password)):
            print('Вы ввели правильный пароль')
            return coll.find_one({"email": email})
        else:
            print('Вы ввели неверный пароль. Повторите попытку')
            return None
    else:
        print('Вы ввели неверный email. Повторите попытку')
        return None


def registrationUser(name, surname, phone, email, password):
    if (not name or not surname or not email or not password):
        print("Не заполнено обязательное поле")
        return None
    emailCheck = coll.find_one({"email": email}, {"email": 1, "_id": 0})
    if (emailCheck):
        print("Такой email уже существует")
        return None
    hashed_password = hash_password(password)
    db.users.insert_one({"name": name, "surname": surname, "phone": phone, "email": email, "password": hashed_password})
    return db.users.find_one(
        {"name": name, "surname": surname, "phone": phone, "email": email, "password": hashed_password})


def createAd(idCreator, date, time, place, quantityPlayers, nameGame, duration, description, recordedPlayers):
    # нет проверки на то, что кол-во игроков число
    if (not date or not time or not place or not quantityPlayers or not nameGame or not duration):
        print("Не заполнено обязательное поле")
        return None
    res = coll.find_one({"_id": ObjectId(idCreator)}, {"password": 0})
    db.ads.insert_one(
        {"idCreator": idCreator, "date": date, "time": time, "place": place, "quantityPlayers": quantityPlayers,
         "nameGame": nameGame, "duration": duration, "description": description, "recordedPlayers": recordedPlayers,
         "dataCreator": res})

    coll1.update_one({"idCreator": idCreator}, {"$set": {"dataCreator": res}})
    return db.ads.find_one(
        {"idCreator": idCreator, "date": date, "time": time, "place": place, "quantityPlayers": quantityPlayers,
         "nameGame": nameGame, "duration": duration, "description": description, "recordedPlayers": recordedPlayers,
         "dataCreator": res})


def RecordingAnAd(idAd, idUser):
    dlina = []
    dlina = coll1.find_one({"_id": idAd['_id']}, {"_id": 0, "recordedPlayers": 1})
    quantityElements = len(dlina['recordedPlayers'])
    dataUser = coll.find_one({"_id": idUser['_id']}, {"password": 0})
    proverka = coll1.find_one({"_id": idAd['_id']}, {"_id": 0, "quantityPlayers": 1})
    if (quantityElements < proverka['quantityPlayers']):
        list3 = []
        list3 = coll1.find_one({"_id": idAd['_id']}, {"_id": 0, "recordedPlayers": 1})
        itog = list3['recordedPlayers']
        #if (dataUser == itog[0]):
         #   print("Такой пользователь уже записан")
          #  return None
        #else:
        for person in itog:
            if (dataUser == person):
                print("Такой пользователь уже записан")
                return None
        res = coll.find_one({"_id": idUser['_id']}, {"password": 0})
        # добавляем пользователя в записанных игроков
        itog.append(res)
        coll1.update_one({"_id": idAd['_id']}, {"$set": {"recordedPlayers": itog}})
        return coll1.find_one({"_id": idAd['_id']})

    else:
        print("Набрано максимальное количество людей")
        return None


def UnsubscribeFromParticipation(idAd, idUser):
    dlina = []
    dlina = coll1.find_one({"_id": idAd['_id']}, {"_id": 0, "recordedPlayers": 1})
    dataRecordedPlayers = dlina['recordedPlayers']
    dataUser = coll.find_one({"_id": idUser['_id']}, {"password": 0})
    for person in dataRecordedPlayers:
        if (dataUser == person):
            dataRecordedPlayers.remove(person)
            coll1.update_one({"_id": idAd['_id']}, {"$set": {"recordedPlayers": dataRecordedPlayers}})


def AdsDateSort():
    cur = db.ads.find().sort([("date", 1)])
    list1 = []
    for doc in cur:
        res = coll.find_one({"_id": ObjectId(doc['idCreator'])}, {"password": 0})
        coll1.update_one({"idCreator": doc['idCreator']}, {"$set": {"dataCreator": res}})
        res1 = coll1.find_one({"idCreator": str(doc['idCreator']), "date": str(doc['date']), "time": str(doc['time']),
                               "place": str(doc['place']), "quantityPlayers": int(doc['quantityPlayers']),
                               "nameGame": str(doc['nameGame']), "duration": str(doc['duration'])})
        list1.append(res1)
    return list1


def SpecificUserAds(idUser):
    cur = coll1.find({"idCreator": str(idUser['_id'])})
    list2 = []
    for doc in cur:
        res = coll.find_one({"_id": ObjectId(doc['idCreator'])}, {"password": 0})
        coll1.update_one({"idCreator": str(idUser['_id'])}, {"$set": {"dataCreator": res}})
        res1 = coll1.find_one({"idCreator": str(idUser['_id']), "date": str(doc['date']), "time": str(doc['time']),
                               "place": str(doc['place']), "quantityPlayers": int(doc['quantityPlayers']),
                               "nameGame": str(doc['nameGame']), "duration": str(doc['duration'])})
        list2.append(res1)
    return list2


def DeleteAd(idCreator, date, time, place, quantityPlayers, nameGame, duration):
    coll1.delete_one({"idCreator": str(idCreator['_id']), "date": date, "time": time, "place": place,
                      "quantityPlayers": quantityPlayers, "nameGame": nameGame, "duration": duration})


def RecordedAds(idUser):
    dataUser = coll.find_one({"_id": idUser['_id']}, {"password": 0})
    cur = coll1.find({"recordedPlayers": dataUser})
    list1 = []
    for doc in cur:
        list1.append(doc)
    return list1