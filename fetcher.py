from __future__ import print_function
import sys

import pprint
import requests
import cfscrape
import datetime
import hashlib
import time
import random

import logging

from platform import system as system_name # Returns the system/OS name
from os import system as system_call       # Execute a shell command

from lxml import html
from lxml import etree

from database import Database



class Fetcher:

    def __init__(self, username, password, proxy, timeout=120):
        self.cookies = None
        self.username = username
        self.password = password
        self.timeout = timeout

        #Connect to database.
        self.db = Database("stormfront")


        self.scraper = cfscrape.create_scraper()

        self.set_proxy(proxy)

        self.logger = logging.getLogger('thread_' + username)
        hdlr = logging.FileHandler('../log/thread_' + username + '.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.WARNING)


    def set_proxy(self, proxy):
        if proxy is not None:
            self.proxy = {
                'http': proxy,
                #'https': proxy,
            }
        else:
            self.proxy = None


    def try_another_proxy(self):
        new_proxy = self.db.set_proxy_down_assign_new(self.proxy['http'], self.username)
        if new_proxy is None:
            raise Exception("Ran out of proxies! Giving up.")

        self.set_proxy(new_proxy)

    def ping(host):
        """
        Returns True if host (str) responds to a ping request.
        Remember that some hosts may not respond to a ping request even if the host name is valid.
        """

        # Ping parameters as function of OS
        parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"

        # Pinging
        return system_call("ping " + parameters + " " + host) == 0


    def get(self,url, **kwargs):
        # Try posting, if it fails, try to ping stormfront.org
        # If successful, it's probably the proxy that's the problem. Change proxy and try again.
        # If failed, its the internet or stormfront. Wait for X minutes then try again.
        # If result returned, check whether we have been logged out.
        # If we have been logged out, call login(). Then try again. If same fail again, user has been blocked: give up().
        # self.scraper.post(url,**kwargs)

        attempts_error_status_code = 20
        attempts_logged_out = 10

        success = False
        while not success:

            try:

                print()
                res = self.scraper.get(url, **kwargs)

                self.logger.info(res.content)
                print()

                if 400 <= res.status_code < 600:
                    self.logger.error("WARNING: Got error status code: %s, reason: %s." % (res.status_code, res.reason))
                    self.logger.error("Not sure what to do. Just saying.")
                    #self.logger.error(res.content)


                if res.status_code is 501:
                    self.logger.error("WARNING: Got error status code: %s, reason: %s."  % (res.status_code, res.reason))
                    if attempts_error_status_code > 0:
                        self.logger.error("Trying to solve by logging in.")
                        self.login()
                        attempts_error_status_code -= 1
                        continue
                    else:
                        self.logger.error("Already tried all attempts. Giving up.")
                        raise Exception("Got status error too many times. Giving up. %s, reason: %s."  % (res.status_code, res.reason))


                if len(html.fromstring(res.content).xpath("//input[@value='guest']")) > 0 or len(
                    html.fromstring(res.content).xpath("//input[@value='Log in']")) > 0:
                    self.logger.error("WARNING: No longer seem to be logged in.")

                    if attempts_logged_out > 0:
                        self.logger.error("Trying to solve by logging in...")
                        self.login()
                        attempts_logged_out -= 1
                        continue
                    else:
                        self.logger.error("Already tried all attempts. Giving up.")
                        raise Exception("Got logged out too many times. Giving up.")

                success = True
                return res

            except requests.exceptions.RequestException:
                self.logger.error("WARNING: Post failed. Trying ping...")

                if self.ping("www.stormfront.org"):
                    #Ping without using proxy. If works, it is probably the proxy that's fucked. Change proxy.
                    self.logger.error("Got response from ping. Probably proxy that's down. Trying another.")
                    self.try_another_proxy()
                else:
                    #No ping, probably internet or SF that's down. Long rest then try again!
                    self.logger.error("No reponse. Probably SF or internet that's down. Resting and then trying again.")
                    time.sleep(random.randint(60,240))



    def login(self):

        self.logger.info("Attempting to by-pass CloudFare bot control...")
        #print(self.scraper.get("https://www.stormfront.org").content)

        #cookie_value, user_agent = cfscrape.get_cookie_string("https://www.stormfront.org")
        fail = True
        while fail:
            try:
                cf_cookie, user_agent = cfscrape.get_tokens("https://www.stormfront.org",proxies=self.proxy)
                fail = False

            except requests.exceptions.RequestException:
                # Probably the proxy!
                self.try_another_proxy()


        #self.cookies = cookie_value

        #request = "Cookie: %s\r\nUser-Agent: %s\r\n" % (cookie_value, user_agent)
        #print(request)

        self.logger.info("Logging in with user %s..." % self.username)

        self.headers = {
            'origin': 'https://www.stormfront.org',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            #        'cookie': 'gsScrollPos=; __cfduid=d3a7beab45ee0e73ce2785686259bcff41491228171; VRcheck=%2C339842%2C; bb2sessionhash=b9433f62d9ed52d02089e2546c415744',
            'pragma': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': user_agent,
            #'cookie': cookie_value,
            #'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'cache-control': 'no-cache',
            'authority': 'www.stormfront.org',
            'referer': 'https://www.stormfront.org/forum/login.php?do=logout',
        }

        params = (
            ('do', 'login'),
        )

        hashedpass = hashlib.md5(self.password.encode('utf-8')).hexdigest()

        data = [
            ('vb_login_username', self.username),
            ('vb_login_password', ''),
            ('s', ''),
            #('securitytoken', '1493064359-73f4ce2367aaca04b9fd76e322c94ec4655866ec'),
            ('securitytoken', 'guest'),
            ('do', 'login'),
            ('vb_login_md5password', hashedpass),#
            ('vb_login_md5password_utf', hashedpass),### hashlib.md5(self.password) ?????????
        ]
        res = self.scraper.post('https://www.stormfront.org/forum/login.php', headers=self.headers, cookies=cf_cookie, params=params, data=data, timeout=self.timeout, proxies = self.proxy)
        #res = self.post(db,'https://www.stormfront.org/forum/login.php', headers=self.headers, cookies=cf_cookie, params=params, data=data, timeout=self.timeout, proxies = self.proxy)

        self.cookies = res.cookies
        requests.utils.add_dict_to_cookiejar(self.cookies, cf_cookie)

        #pprint.pprint(self.cookies)

        res.raise_for_status()


    def get_user_friendlist(self, userid):
        params = {
            'tab': 'friends',
            'u': userid,
            'pp': '10000',
            'page': '1',
        }

        r = self.get('https://www.stormfront.org/forum/member.php', headers=self.headers, params=params,cookies=self.cookies, timeout=self.timeout, proxies=self.proxy)

        tree = html.fromstring(r.content)
        names = tree.xpath('//a[@class="bigusername"]')
        with_ids = [name.attrib['href'].split("=")[1] for name in names]

        self.db.add_friends(userid,with_ids)

    @staticmethod
    def clean_text_string(string):
        string = string.replace("\\n"," ")
        string = string.replace("\\r", " ")
        string = string.replace("\\t", " ")
        return ' '.join(string.split())

    def get_user_info(self, userid):
        params = {'u': userid}
        #r = self.scraper.get('https://www.stormfront.org/forum/member.php',headers=self.headers, params=params, cookies=self.cookies, timeout=self.timeout, proxies = self.proxy)
        r = self.get('https://www.stormfront.org/forum/member.php', headers=self.headers, params=params,
                             cookies=self.cookies, timeout=self.timeout, proxies=self.proxy)
        tree = html.fromstring(r.content)


        names = tree.xpath('//*[@id="username_box"]/h1//*/text()')

        if len(names) == 0:
            print("WARNING: Failed getting user id %s" % userid)
            self.db.set_user_failed(userid)

        else:
            name = names[0]

            ministat = tree.xpath('//div[@id="collapseobj_stats_mini"]')[0]
            profile = tree.xpath('//div[@id="collapseobj_aboutme"]')[0]

            profiletext = str(etree.tostring(profile))
            ministattext = str(etree.tostring(ministat))

            #Clean out multiple line breaks and whitespaces
            profiletextonly = Fetcher.clean_text_string(str(etree.tostring(profile, method='text')))
            ministattextonly = Fetcher.clean_text_string(str(etree.tostring(ministat, method='text')))

            print("name", name)
            print("ministat", ministat)
            print("profile", profile)
            print("ministattext", ministattextonly)
            print("profiletext", profiletextonly)

            data = {'id': userid, 'name': name, 'ministat': profiletext, 'profile': ministattext,
                    'ministattext': profiletextonly, 'profiletext': ministattextonly}
            self.db.add_user(userid,data)


    @staticmethod
    def parse_date(datestr):
        datestr = datestr.strip().lower()
        if datestr.startswith("yesterday"):
            #e.g. Yesterday, 05:34 PM
            timestr = datestr[len("yesterday,"):].strip()
            time = datetime.datetime.strptime(timestr, "%I:%M %p")

            yesterday = datetime.datetime.today() - datetime.timedelta(1)

            return yesterday.replace(hour=time.hour, minute=time.minute,second=0,microsecond=0)

        elif datestr.startswith("today"):
        #Today, 06:03 AM
            timestr = datestr[len("today,"):].strip()
            time = datetime.datetime.strptime(timestr, "%I:%M %p")

            return datetime.datetime.today().replace(hour=time.hour, minute=time.minute,second=0,microsecond=0)
        else:
            # 05-29-2017, 01:41 PM
            return datetime.datetime.strptime(datestr, "%m-%d-%Y, %I:%M %p")




    def fetch_thread_page(self,tid,page):

        headers = {
            'pragma': 'no-cache',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'cache-control': 'no-cache',
            'authority': 'www.stormfront.org',
            #  'cookie': cookie, #'gsScrollPos=;__cfduid=d3a7beab45ee0e73ce2785686259bcff41491228171; VRcheck=%2C339842%2C;bb2lastvisit=1493064370; bb2lastactivity=0; bb2sessionhash=a3ef28efe4019980f3c84ed019b33386',
            'referer': 'https://www.stormfront.org/forum/login.php?do=login',
        }
        params = (
        )
        #r = self.scraper.get("https://www.stormfront.org/forum/t{}-{}/".format(tid,page),
        #                 headers=headers, params=params, cookies=self.cookies, timeout=self.timeout)
        r = self.get("https://www.stormfront.org/forum/t{}-{}/".format(tid,page),
                         headers=headers, params=params, cookies=self.cookies, timeout=self.timeout)
        tree = html.fromstring(r.content)

        #Does thread exist?
        if "".join(tree.xpath("//td[@class='panelsurround']/div[@class='panel']/div//text()")).count("No Thread specified.") > 0:
            #thread does not exist
            print("No such thread")
            self.db.thread_failed(tid)
            return False

        else:
            messages = tree.xpath("//div[@id='posts']//table[starts-with(@id,'post')]")

            #First page! Create thread and forums
            if page == 1:
                forums = tree.xpath("//span[@class='navbar']/a")

                # create forums
                parentid = None
                for fi in range(1, len(forums)):
                    forumid = forums[fi].attrib["href"].split("/forum/f")[1][:-1]
                    forumtitle = forums[1].xpath("span/text()")[0]

                    data = {'id': forumid, 'title': forumtitle, 'parent': parentid}
                    self.db.add_forum(forumid,data)

                    parentid = forumid


                threadtitle = tree.xpath("//td[@class='navbar']//strong/span[@itemprop='title']/text()")[0]
                threaddate = ''.join(messages[0].xpath('.//td[@class="thead"][1]/text()')).strip()
                threaddateparse = Fetcher.parse_date(threaddate)

                data = {'title': threadtitle, 'forum': parentid, 'createdate': threaddateparse, 'createdatestr': threaddate  }
                self.db.add_thread(tid,data)


            #Process posts
            i = 0
            for message in messages:
                i = i + 1

                messageid = message.attrib['id'].split('t')[1]
                authorid = message.xpath('.//*[@class="bigusername"]')[0].attrib['href'].split('=')[1]
                datestr = ''.join(message.xpath('.//td[@class="thead"][1]/text()')).strip()
                dateparse = Fetcher.parse_date(datestr)
                #dateparse = datetime.datetime.strptime(datestr,"%m-%d-%Y, %I:%M %p")

                fullmessage = message.xpath(".//*[starts-with(@id,'post_message_')]")[0]
                fullmessagehtml = etree.tostring(fullmessage)
                cleanmessage = " ".join(fullmessage.xpath("./text()|./*[not(self::div)]//text()")).strip()

                signature = " ".join(message.xpath(".//div[@class='hidesig']//text()")).strip()
                title = message.xpath(".//td[@class='alt1']/div/strong/text()")[0]


                quote = fullmessage.xpath(".//div/table//tr/td/div[1]/a")
                hasquote = False
                quoteofpostid, quoteofusername,quotehtml,quotetxt  = None,None,None,None
                if len(quote) > 0:
                    hasquote = True
                    quoteofpostid = quote[0].attrib["href"].split("post")[1]
                    quoteofusername = fullmessage.xpath(".//div/table//tr/td/div[1]/strong/text()")[0]
                    quotehtml = etree.tostring(fullmessage.xpath(".//div/table//tr/td/div[2]")[0])
                    quotetxt = " ".join(fullmessage.xpath(".//div/table//tr/td/div[2]//text()"))


                #ADD TO DATABASE
                data = {'id': messageid, 'authorid': authorid, 'posteddate': dateparse,
                        'fullmessagehtml': fullmessagehtml, 'cleanmessage': cleanmessage, 'signature': signature,
                        'title': title, 'hasquote': hasquote, 'quoteofpostid': quoteofpostid, 'quoteofusername': quoteofusername,
                        'quotehtml': quotehtml,'quotetxt': quotetxt}

                #pprint.pprint(data)
                self.db.add_post(messageid, data)

            #Is there a next page?
            return len(tree.xpath("//td[@class='alt1']/a[@rel='next']")) > 0

if __name__ == '__main__':
    fetch = Fetcher("wickedness","tintolito","86.62.108.219:53281")
    fetch.login(None)
    #fetch.fetch_thread_page(1213459,1,None)
    fetch.get_user_friendlist(1,None)

