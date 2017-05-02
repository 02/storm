import pymongo
import datetime
import pprint
import bson
from pymongo import MongoClient
from random import randint
import time


class Database:
    def __init__(self, dbname):
        print("Connecting to database")
        self.client = MongoClient()
        self.db = self.client[dbname]


    def upsert_user(self, id, data):
        result = self.db.users.update({"id": id}, data, True)

        #if result['updatedExisting']:
         #   print('User already existed. Updated.')

    def upsert_thread(self,id,data):
        result = self.db.threads.update({"id": id}, data, True)

    def upsert_post(self,id,data):
        result = self.db.posts.update({"id": id}, data, True)

    def get_random_proxy_and_mark_used(self):
        nrproxies = self.db.proxy.find().count()
        randomNr = randint(1,nrproxies)
        ret = self.db.proxy.find({'used': False, 'broken': False}).limit(-1).skip(randomNr).next()

        #Set used
        self.db.proxy.update({"id": id}, {'$set',{'used',True}})


    def set_proxy_down(self,proxyip,user_id):
        self.db.proxy.update({"id": id}, {'$set', {'broken', True}})

        proxy = pop_proxy()
        self.db.proxy.update({"id": id}, {'$set', {'broken', True}})
        #TODO: Get a new proxy for the associated user.


    def get_random_login_and_mark_used(self):
        nr = self.db.login.find().count()
        randomNr = randint(1,nr)
        ret = self.db.login.find({'used': False, 'broken': False}).limit(-1).skip(randomNr).next()

        #Set used
        self.db.login.update({"id": id}, {'$set',{'used',True}})

        #TODO: If the login doesnt have a proxy, get a random unused proxy and
        # attach to it. Goal: We dont want to connect to all users from all proxies, but
        # always connect each user to a unique proxy.


    def populate_threads_to_be_fetched(self,fromnr,tonr):
        #Add all
        for i in range(fromnr,tonr):
            self.db.thread.update({'id': i},{'id': i},True)


    def pop_thread(self):
        nr = self.db.login.find().count()
        randomNr = randint(1, nr)
        ret = self.db.login.find().limit(-1).skip(randomNr).next()

        # Set used
        self.db.login.update({"id": id}, {'$set', {'used', True}})
        return ret

    def pop_proxy(self):
        ret = self.db.proxy.find_one({"broken": {"$ne": True}, "used": {"$ne": True} })
        return ret

    def pop_login(self):
        ret = self.db.login.find_one({"used": {"$ne": True}})
        #If it doesnt have a proxy attached, fetch one

        



    def populate_users_to_be_fetched(self, fromnr, tonr):
        # Add all
        for i in range(fromnr, tonr):
            self.db.users.update({'id': i}, {'id': i}, True)