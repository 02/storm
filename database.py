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

    def get_all_login(self):
        ret = self.db.login.find({'broken': None})

        logins = []
        for login in ret:
            if login['proxy'] is None:
                login['proxy'] = self.assign_login_a_random_unused_proxy(login['username'])
            logins.append(login)

        # Set used
        self.db.login.update({}, {'$set': {'used': datetime.utcnow()}})

        return logins


    def pop_login(self):
        nr = self.db.login.find().count()

        if nr == 0:
            return None

        ret = self.db.login.find({'used': None, 'broken': None}).limit(-1).skip(randint(0, nr-1)).next()

        username = ret['username']

        # Set used
        self.db.login.update({"username": username}, {'$set': {'used': datetime.utcnow()}})

        if ret['proxy'] is None:
            ret['proxy'] = self.assign_login_a_random_unused_proxy(username)

        return ret

    def assign_login_a_random_unused_proxy(self,username):
        nrproxies = self.db.proxy.find().count()
        ret = self.db.proxy.find({'used': None, 'broken': None}).limit(-1).skip(randint(0,nrproxies-1)).next()

        ip = ret['ip']

        #Set used
        self.db.proxy.update({"ip": ip}, {'$set': {'used': datetime.utcnow()}})

        #Assign to user
        self.db.login.update({"username": username}, {'$set': {'proxy': ip}})

        return ip

    def set_proxy_down_assign_new(self,ip,username):
        self.db.proxy.update({"ip": ip}, {'$set': {'broken': datetime.utcnow()}})
        return self.assign_login_a_random_unused_proxy(username)

    ######### Thread management
    #Data structure
    #Thread:
    # id
    # title
    # parent_id
    # processed: None or timestamp

    def add_thread(self,tid,data):
        data['inserted'] = datetime.utcnow()
        data['status'] = 2
        result = self.db.thread.update({"id": tid}, data, True)


    def thread_completed(self,tid):
        result = self.db.thread.update({"id": tid}, {'$set': {'status': 2, 'completed': datetime.utcnow()}})

    def thread_failed(self,tid):
        result = self.db.thread.update({"id": tid}, {'$set': {'status': -1, 'completed': datetime.utcnow()}})

    def populate_threads_to_be_fetched(self,fromnr,tonr):
        #Add all
        for i in range(fromnr,tonr):
            self.db.thread.update({'id': i},{'$setOnInsert':{'id': i,'status': 0}},True)

    def pop_thread(self):
        nr = self.db.thread.find({'status': 0}).count()

        if nr == 0:
            return None

        ret = self.db.thread.find({'status': 0}).limit(-1).skip(randint(0, nr-1)).next()
        tid = ret['id']

        # Set used
        self.db.thread.update({"id": tid}, {'$set': {'status': 1, 'processing_start': datetime.utcnow()}})
        return tid


    ## Posts
    def add_post(self,pid,data):
        print("Adding post ", pid, " to database")
        data['inserted'] = datetime.utcnow()
        result = self.db.post.update({"id": pid}, data, True)

    #### Users management

    ## Friends:
    # id1
    # id2

    # User:
    # id,username,inserted, ..
    # status: 0 - non-processed, 1 - under processing, -1 error, 2 processed

    def pop_user(self):
        nr = self.db.user.find({'status': 0}).count()
        if nr == 0:
            return None

        ret = self.db.user.find({'status': 0}).limit(-1).skip(randint(0, nr - 1)).next()

        self.set_user_processing(ret['id'])
        return ret['id']



    def set_user_processing(self,uid):
        result = self.db.user.update({"id": uid}, {'$set': {'processing_started': datetime.utcnow(), 'status': 1}})

    def set_user_failed(self,uid):
        result = self.db.user.update({"id": uid}, {'$set': {'processing_finished': datetime.utcnow(), 'status': -1}})

    def populate_users_to_be_fetched(self, fromnr, tonr):
        # Add all
        for i in range(fromnr, tonr):
            self.db.user.update({'id': i}, {'$setOnInsert': {'id': i,'status': 0}}, True)

    def add_user(self,uid,data):
        result = self.db.user.update({"id": uid}, data, True)
        result = self.db.user.update({"id": uid}, {'$set': {'processing_finished': datetime.utcnow(), 'status': 2} })

    def add_friends(self,user_id1,with_users):
        for user_id2 in with_users:
            data = {"id1": user_id1,"id2": user_id2}
            self.db.friend.update(data, data, True)


    ## FORUMS
    #forum: id, title, parentid

    def add_forum(self,fid,data):
        self.db.forum.update({"id": fid}, data, True)
