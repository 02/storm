

from multiprocessing import Pool
import sys
import database
import os

db = None
fetcher = None


def populate_database_with_thread_interval(fromid,toid):
    #Add to thread database all number between fromid to toid.
    db.populate_threads_to_be_fetched(fromid,toid)

def populate_database_with_user_interval(fromid, toid):
    # Add to user database all number between fromid to toid.
    db.populate_users_to_be_fetched(fromid, toid)

def fetch_random_thread():
    #Get random unprocessed thread from database
    return db.pop_thread()

def fetch_random_user():
    return db.pop_user()


def fetch_users():
    #Repeat:
        # Login
        #Repeat:
            # Take a random un-fetched user from database, mark as being under processing
            # get_user_friendlist(1, cookie)
            # get_user_info(336591, cookie)
            # Pause randomly
            # If logged out, quit loop
        #sleep a bit


def fetch_thread():
    # Repeat:
        # Login
        # Repeat:
            # Take a random un-fetched thread from database, mark as being under processing
            # Fetch thread fetch_thread_page(cookie, 1208742, 1) #1208742
            # Pause randomly
        #sleep a bit


def get_random_proxy():
# call db.get_random_proxy_and_mark_used()
# return proxy
# if return null, throw error

def set_proxy_down(ip):
    db.

# db.set_proxy_down(ip)

def get_random_user():


# call db.get_random_user_mark_used()
# if return null, throw error

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

def populate_user_database(fromnr,tonr):
    db.populate_threads_to_be_fetched(fromnr,tonr)

def fetch_all_users():



def print_instructions():
    print("storm.py <COMMAND>")
    print("Possible commands:")
    print("--clean-database \t\t\t Empties the specified database and starts over.")
    print("--start-get-users <from_id> <to_id> \t\t\t Start download of users.")
    print("--continue-get-users \t\t\t Continue previous user download.")
    print("--start-get-threads <from_id> <to_id> \t\t\t Start download of threads.")
    print("--continue-get-threads \t\t\t Continue previous user download.")

    print("--add-proxy <IP> \t\t\t Add proxy to proxy list.")
    print("--add-login <username> <password> \t\t\t Add new user to login list.")
    print("--monitor-new-posts \t\t\t Continuously scrape new posts.")
    print("--monitor-new-users \t\t\t Continuously scrape new users.")

def main():

    if len(sys.argv) < 2:
        print("Please provide arguments.")
        print_instructions()
        exit()

    tag = sys.argv[1]
    global db
    db = database.Database("stormfront")

    if sys.argv[2].strip() == "--clean-database":
        if query_yes_no("Are you sure you want to empty database?", "no"):
            print('Cleaning database...')
            db.drop_all()
        else:
            print("Leaving database intact.")

    elif sys.argv[2].strip() == "--start-get-users":
        if len(sys.argv) != 4:
            print_instructions()
            exit()

        print("Populating user database...")

        populate_user_database(int(sys.argv[3]),int(sys.argv[4]))
        fetch_all_users()


    elif sys.argv[2].strip() == "--continue-get-users":
        print("Continuing user download...")
        fetch_all_users()

    elif sys.argv[2].strip() == "--start-get-threads":

        if len(sys.argv) != 4:
            print_instructions()
            exit()

        print("Populating thread database...")
        populate_thread_database(int(sys.argv[3]), int(sys.argv[4]))
        fetch_all_threads()

    elif sys.argv[2].strip() == "--continue-get-users":

        print("Continuing user download...")

        fetch_all_users()

    elif sys.argv[2].strip() == "--add-proxy":

        if len(sys.argv) != 3:
            print_instructions()
            exit()

        add_proxy(sys.argv[3])

#TODO
    print("--add-login <username> <password> \t\t\t Add new user to login list.")
    #print("--monitor-new-posts \t\t\t Continuously scrape new posts.")
    print("--monitor-new-users \t\t\t Continuously scrape new users.")



    else:
        print("Unknown instructions.")
        print_instructions()



    cookie = login()
    #get_user_friendlist(1, cookie)
    #get_user_info(336591, cookie)
    fetch_thread_page(cookie, 1208742, 1) #1208742

    #there are 242542 users, 340190 ids
    #2 fetch per user. 700,000 fetches.


if __name__ == '__main__':
    main()
