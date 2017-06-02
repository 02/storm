from multiprocessing import Pool
import multiprocessing
import sys
import os
import random
import time

import database
import fetcher

db = None


def fetch_all_users_single():
    login = db.pop_login()
    fetch_all_users(login['username'], login['password'], login['proxy'])

def fetch_all_users_parallel():
    logins = db.get_all_login()
    jobs = []
    for login in logins:
        p = multiprocessing.Process(target=fetch_all_users, args=(login['username'],login['password'],login['proxy']))
        jobs.append(p)
        p.start()

    print("Out of loop.")

def fetch_all_users(username,password,proxy):
    fetch = fetcher.Fetcher(username, password, proxy)
    fetch.login()
    fetch.fetch_all_users()


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


def fetch_all_threads(username,password,proxy):
    fetch = fetcher.Fetcher(username, password, proxy)
    fetch.login()
    fetch.fetch_all_threads()

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

    print("--populate-threads <from_id> <to_id> \t\t\t Set user ids to download.")
    print("--get-users \t\t\t Continue user download. All users in parallel.")
    print("--get-users-single \t\t\t Continue user download. Single thread.")

    print("--populate-threads <from_id> <to_id> \t\t\t Set threads to download.")
    print("--get-threads-single \t\t\t Continue previous user download.")
    print("--get-threads-parallel \t\t\t Continue previous user download.")

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

    elif command == "--populate-users":
        if len(sys.argv) != 4:
            print_instructions()
            exit()
        print("Populating user database...")
        db.populate_users_to_be_fetched(int(sys.argv[2]),int(sys.argv[3]))

    elif command == "--get-users":
        print("Continuing user download parallelized...")
        fetch_all_users_parallel()

    elif command == "--get-users-single":
        print("Continuing user download single thread...")
        fetch_all_users_single()


    elif command == "--get-threads-single":
        print("Continuing thread download...")
        fetch_all_thread_single()

    elif command == "--get-threads":
        print("Continuing thread download...")
        fetch_all_threads_parallel()

    elif command == "--populate-threads":
        if len(sys.argv) != 4:
            print_instructions()
            exit()

        print("Populating thread database...")

        # Add to thread database all number between fromid to toid.
        db.populate_threads_to_be_fetched(int(sys.argv[2]), int(sys.argv[3]))





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
