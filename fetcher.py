
import pprint
import requests
import cfscrape
import datetime
import hashlib

from lxml import html
from lxml import etree



class Fetcher:

    def __init__(self, username, password, proxy,timeout=120):
        self.cookies = None
        self.username = username
        self.password = password
        self.timeout = timeout

        self.scraper = cfscrape.create_scraper()


        if proxy is not None:
            self.proxy = {
                'https': proxy,
                'https': proxy,
            }
        else:
            self.proxy = None


    def login(self):

        print("getting main page")
        #print(self.scraper.get("https://www.stormfront.org").content)

        cookie_value, user_agent = cfscrape.get_cookie_string("https://www.stormfront.org")

        request = "Cookie: %s\r\nUser-Agent: %s\r\n" % (cookie_value, user_agent)
        print request

        print("Trying to log in!")

        headers = {
            'origin': 'https://www.stormfront.org',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            #        'cookie': 'gsScrollPos=; __cfduid=d3a7beab45ee0e73ce2785686259bcff41491228171; VRcheck=%2C339842%2C; bb2sessionhash=b9433f62d9ed52d02089e2546c415744',
            'pragma': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': user_agent,
            'cookie': cookie_value,
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

        res = self.scraper.post('https://www.stormfront.org/forum/login.php', headers=headers, params=params, data=data, timeout=self.timeout)
        cookie = res.cookies

        res.raise_for_status()

        pprint.pprint(res)

        self.cookies = cookie
        #return cookie


    def get_user_friendlist(self, userid):
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
            ('tab', 'friends'),
            ('u', userid),
            ('pp', '10000'),
            ('page', '1'),
        )

        r = self.scraper.get('https://www.stormfront.org/forum/member.php',
                         headers=headers, params=params, cookies=self.cookies, timeout=self.timeout)

        tree = html.fromstring(r.content)
        names = tree.xpath('//a[@class="bigusername"]')
        ids = [name.attrib['href'].split("=")[1] for name in names]

        print('bp')
        #SAVE TO DATABASE

    def get_user_info(self, userid):
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
            ('u', userid),
        )

        r = self.scraper.get('https://www.stormfront.org/forum/member.php',
                         headers=headers, params=params, cookies=self.cookies, timeout=self.timeout)

        tree = html.fromstring(r.content)

        name = tree.xpath('//*[@id="username_box"]/h1//*/text()')[0]
        ministat = tree.xpath('//div[@id="collapseobj_stats_mini"]')[0]
        profile = tree.xpath('//div[@id="collapseobj_aboutme"]')[0]

        profiletext = etree.tostring(profile)
        ministattext = etree.tostring(ministat)

        print("name", name)
        print("ministat", ministat)
        print("profile", profile)




    def fetch_thread_page(self,tid,page,db):



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
        r = self.scraper.get("https://www.stormfront.org/forum/t{}-{}/".format(tid,page),
                         headers=headers, params=params, cookies=self.cookies, timeout=self.timeout)
        tree = html.fromstring(r.content)

        #Does thread exist?
        if "".join(tree.xpath("//td[@class='panelsurround']/div[@class='panel']/div//text()")).count("No Thread specified.") > 0:
            #thread does not exist
            print("No such thread")

            return False

        else:
            if page == 1:
                print("This is first page of thread. Will add thread info to db!")
                print("TODO TODO TODO!")
                #TODO: extract thread info!


            #Process posts
            i = 0
            for message in tree.xpath("//div[@id='posts']//table[starts-with(@id,'post')]"):
                i = i + 1

                messageid = message.attrib['id'].split('t')[1]
                authorid = message.xpath('.//*[@class="bigusername"]')[0].attrib['href'].split('=')[1]
                datestr = ''.join(message.xpath('.//td[@class="thead"][1]/text()')).strip()
                dateparse = datetime.datetime.strptime(datestr,"%m-%d-%Y, %I:%M %p")

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

                print(i, messageid, authorid, dateparse, fullmessagehtml, cleanmessage, signature, title)
                if hasquote:
                    print(quoteofusername, quoteofpostid, quotehtml, quotetxt)

                #ADD TO DATABASE
                data = {'id': messageid, 'authorid': authorid, 'posteddate': dateparse, 'fullmessage': fullmessage,
                        'fullmessagehtml': fullmessagehtml, 'cleanmessage': cleanmessage, 'signature': signature,
                        'title': title, 'hasquote': hasquote, 'quoteofpostid': quoteofpostid, 'quoteofusername': quoteofusername,
                        'quotehtml': quotehtml,'quotetxt': quotetxt}

                db.add_post(messageid, data)


            #Is there a next page?
            return len(tree.xpath("//td[@class='alt1']/a[@rel='next']")) > 0
