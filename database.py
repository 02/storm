import pymongo
from datetime import datetime
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


    def drop_all_data(self):
        self.db.post.drop()
        self.db.thread.drop()
        self.db.user.drop()

    def drop_login_and_proxy(self):
        self.db.login.drop()
        self.db.proxy.drop()

    ## LOGIN AND PROXY MANAGEMENT

    ### DATABASE STRUCTURE: ####
    # Proxy:
    ## ip: string <#key>
    ## broken: None or timestamp
    ## used: None or timestamp

    # Login:
    # username: string <#key>
    # password: string
    # used: True/False
    # proxy: string  ##ip to current proxy used

    #### FUNCTIONS: ###
    # get_login():
    # Take a random unused login. If it doesn't have an IP to it, assign_user_a_random_unused_proxy(userid)

    # assign_user_a_random_unused_proxy(userid)
    # Take a random unused proxy. Set as proxy for userid. Return.

    # proxy_down(proxyid,username):
    # set broken: True for proxy.
    # assign_user_a_random_unused_proxy()
    # return new proxy

    def set_all_logins_not_used(self):
        self.db.login.update({}, {'$set': {'used': None}})

    def push_login(self, username, password):
        data = {"username":username,"password":password,"used": None, "proxy": None}
        result = self.db.login.update({"username": username}, data, True)

        if result['updatedExisting']:
            print('User already existed. Updated.')

    def push_proxy(self, ip):
        data = {"ip":ip, "broken": None,"used": None}
        result = self.db.proxy.update({"ip": ip}, data, True)

    def set_login_not_used(self,username):
        self.db.login.update({"username": username}, {'$set': {'used': None}})

    def pop_login(self):
        nr = self.db.login.find().count()
        print('nr users',nr)
        ret = self.db.login.find({'used': None, 'broken': None}).limit(-1).skip(randint(0, nr-1)).next()

        username = ret['username']

        # Set used
        self.db.login.update({"username": username}, {'$set': {'used': datetime.now()}})

        if ret['proxy'] is None:
            ret['proxy'] = self.assign_login_a_random_unused_proxy(username)

        return ret

    def assign_login_a_random_unused_proxy(self,username):
        nrproxies = self.db.proxy.find().count()
        ret = self.db.proxy.find({'used': None, 'broken': None}).limit(-1).skip(randint(0,nrproxies-1)).next()

        ip = ret['ip']

        #Set used
        self.db.proxy.update({"ip": ip}, {'$set': {'used': datetime.now()}})

        #Assign to user
        self.db.login.update({"username": username}, {'$set': {'proxy': ip}})

        return ip

    def set_proxy_down(self,ip,username):
        self.db.proxy.update({"ip": ip}, {'$set': {'broken': datetime.now()}})
        return self.assign_login_a_random_unused_proxy(username)

    ######### Thread management
    #Data structure
    #Thread:
    # id
    # title
    # parent_id
    # processed: None or timestamp

    def add_thread(self,id,data):
        result = self.db.thread.update({"id": id}, data, True)
        result = self.db.thread.update({"id": id}, {'$set': {'inserted': datetime.now()}})

    def thread_completed(self,id):
        result = self.db.thread.update({"id": id}, {'$set': {'completed': datetime.now()}})

    def populate_threads_to_be_fetched(self,fromnr,tonr):
        #Add all
        for i in range(fromnr,tonr):
            self.db.thread.update({'id': i},{'id': i},True)

    def pop_thread(self):
        nr = self.db.thread.find({'processing_start', {'$exists': False}}).count()
        randomNr = randint(1, nr)
        ret = self.db.thread.find({'processing_start', {'$exists': False}}).limit(-1).skip(randomNr).next()

        # Set used
        self.db.thread.update({"id": id}, {'$set': {'processing_start': datetime.now()}})
        return ret

    ## Posts
    def add_post(self,id,data):
        result = self.db.post.update({"id": id}, data, True)
        result = self.db.post.update({"id": id}, {'$set': {'inserted': datetime.now()}})

    #### Users management

    ## Friends:
    # id1
    # id2

    # User:
    # id,username,inserted, ..

    def populate_users_to_be_fetched(self, fromnr, tonr):
        # Add all
        for i in range(fromnr, tonr):
            self.db.user.update({'id': i}, {'id': i}, True)

    def add_user(self,id,data):
        result = self.db.user.update({"id": id}, data, True)
        result = self.db.user.update({"id": id}, {'$set': {'inserted': datetime.now()}})

    def add_friends(self,user_id1,user_id2):
        data = {"id1": user_id1,"id1": user_id2}
        result = self.db.user.update(data, data, True)
