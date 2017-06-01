from multiprocessing import Pool
import multiprocessing
import sys
import os
import random
import time

import database
import fetcher

short_pause_min = 5
short_pause_max = 10
long_pause_min = 30
long_pause_max = 60

db = None


def short_pause():
    time.sleep(random.randint(short_pause_min,short_pause_max))


def long_pause():
    time.sleep(random.randint(long_pause_min,long_pause_max))

def fetch_all_users():

    login = db.pop_login()
    fetch = fetcher.Fetcher(login['username'], login['password'], login['proxy'])
    fetch.login()

    print("Beginning user download...")
    user_id = db.pop_user()
    while user_id is not None:
        print("Scraping user %s..." % user_id)

        fetch.get_user_friendlist(user_id)
        fetch.get_user_info(user_id)

        print("Taking short rest...")
        short_pause()
        user_id = db.pop_user()

    print("User scraping completed.")



def fetch_all_threads_parallel():
    logins = db.get_all_login()
    jobs = []
    for login in logins:
        p = multiprocessing.Process(target=fetch_all_threads, args=(login['username'],login['password'],login['proxy']))
        jobs.append(p)
        p.start()

    print("Out of loop.")


def fetch_all_thread_single():
    login = db.pop_login()
    fetch_all_threads(login['username'], login['password'], login['proxy'])

def fetch_all_threads(username, password, proxy):

    #login = db.pop_login()
    #fetch = fetcher.Fetcher(login['username'], login['password'], login['proxy'])
    fetch = fetcher.Fetcher(username, password, proxy)
    fetch.login()

    print("### Beginning thread download with user %s..." % username)
    thread_id = db.pop_thread()
    while thread_id is not None:
        print("## %s Scraping thread %s..." % (username, thread_id))

        page = 1
        has_more_pages = True
        while has_more_pages:
            print("# %s Scraping thread %s, page %s... " % (username, thread_id, page))
            has_more_pages = fetch.fetch_thread_page(thread_id, page)
            page += 1
            short_pause()

            thread_id = db.pop_thread()

    print("Thread scraping completed.")

    #
    # login = db.pop_login()
    # fetch = fetcher.Fetcher(login['username'], login['password'], login['proxy'])
    #
    # fetch.login()
    #
    # while(True):
    #     thread = db.pop_thread()
    #     id = thread['id']
    #
    #     page = 1
    #     has_more_pages = True
    #     while has_more_pages:
    #         has_more_pages = fetch.fetch_thread_page(id, page, db)
    #         page += 1
    #         short_pause()
    #
    #     db.thread_completed(id)
    # Repeat:
        # Login
        # Repeat:
            # Take a random un-fetched thread from database, mark as being under processing
            # Fetch thread fetch_thread_page(cookie, 1208742, 1) #1208742
            # Pause randomly
        #sleep a bit


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


### Callable functions


def print_instructions():
    print("storm.py <COMMAND>")
    print("Possible commands:")
    print("--clean-data \t\t\t Removes all scraped data.")
    print("--clean-login \t\t\t Removes all logins and proxies.")
    print("--start-get-users <from_id> <to_id> \t\t\t Start download of users.")
    print("--continue-get-users \t\t\t Continue previous user download.")
    print("--start-get-threads <from_id> <to_id> \t\t\t Start download of threads.")
    print("--continue-get-threads \t\t\t Continue previous user download.")

    print("--add-proxy <IP> \t\t\t Add proxy to proxy list.")
    print("--add-login <username> <password> \t\t\t Add new user to login list.")
    print("--monitor-new-posts \t\t\t Continuously scrape new posts. NOT YET IMPLEMENTED.")
    print("--monitor-new-users \t\t\t Continuously scrape new users. NOT YET IMPLEMENTED.")


def test(arg):
    for i in range(100):
        print(arg, i)
        time.sleep(random.random())

def main():
    print("Starting up!")

    if len(sys.argv) < 2:
        print("Please provide arguments.")
        print_instructions()
        exit()

    command = sys.argv[1].strip()
    global db
    db = database.Database("stormfront")

    db.set_all_logins_not_used()


   # print(command,sys.argv[2].strip())

    if command == "--clean-data":
        if query_yes_no("Are you sure you want to empty database?", "no"):
            print('Cleaning database...')
            db.drop_all_data()
        else:
            print("Leaving database intact.")

    elif command == "--clean-login":
        if query_yes_no("Are you sure you want to empty database?", "no"):
            print('Cleaning database...')
            db.drop_login_and_proxy()
        else:
            print("Leaving database intact.")

    elif command == "--start-get-users":
        if len(sys.argv) != 4:
            print_instructions()
            exit()

        print("Populating user database...")

        db.populate_users_to_be_fetched(int(sys.argv[2]),int(sys.argv[3]))
        fetch_all_users()


    elif command == "--continue-get-threads":
        print("Continuing thread download...")
        fetch_all_thread_single()

    elif command == "--start-get-threads":

        if len(sys.argv) != 4:
            print_instructions()
            exit()

        print("Populating thread database...")

        # Add to thread database all number between fromid to toid.
        db.populate_threads_to_be_fetched(int(sys.argv[2]), int(sys.argv[3]))

        fetch_all_thread_single()

    elif command == "--continue-get-users":

        print("Continuing user download...")

        fetch_all_users()

    elif command == "--add-proxy":

        if len(sys.argv) != 3:
            print_instructions()
            exit()

        db.push_proxy(sys.argv[2])

    elif command == "--add-login":
        if len(sys.argv) != 4:
            print_instructions()
            exit()

        db.push_login(sys.argv[2],sys.argv[3])


    #TODO later
    #print("--monitor-new-posts \t\t\t Continuously scrape new posts.")
    #print("--monitor-new-users \t\t\t Continuously scrape new users.")


    else:
        print("Unknown instructions.")
        print_instructions()



    #cookie = login()
    #get_user_friendlist(1, cookie)
    #get_user_info(336591, cookie)
    #fetch_thread_page(cookie, 1208742, 1) #1208742

    #there are 242542 users, 340190 ids
    #2 fetch per user. 700,000 fetches.


if __name__ == '__main__':
    main()
