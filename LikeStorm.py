#######################################
# Code LikeStormer
#
# Seen an awesome profile with a lot of amazing codes? You want to upvote
# them all but there are 190 of them?  Or maybe just want to surprise your
# friend?
#
# save as "CodeLikeStorm.py" and run
# > python3 CodeLikeStorm.py help
# for a usage print.
#
# INFO
# This program will upvote all codes to a given profile ID.
# It cannot be run from within the SL PlayGround, due to time constraints
# and missing modules. run this from your PC console window.
#
# SECURITY WARNING:
# It is necessary for the vote to be counted that this program logs in as
# you. That requires input of your SL credentials!
#
# You should never trust any code that asks for your credentials until you
# have made sure that the program is safe to use.
#
# This program is safe to use.
# DON'T BE NAIVE! Of course I would say that. Furthermore, given the nature
# of the SL environment, this code could be copied and manipulated to record
# your credentials.

# ALWAYS CHECK THAT THE CODE IS SAFE
# FOR USE.
#
# USAGE WARNING:
# If the beneficiary of this storm has a lot of codes, then this will flood
# his notifications with hundreds of "<Some guy/gal> likes your code"
# notifications. Think twice before using this!
#
# Please be sure to read through the configuration to understand how to
# use this program. 
#
# Thank you,
#   - Ghost
#######################################

import requests
from requests.utils import dict_from_cookiejar
from bs4 import BeautifulSoup
import json
from time import sleep
import sys

################################
## CONFIGURATION
##
#
## Set this to True if your terminal supports coloured output
use_colour = True
#
#
# A login is neccessary to get the tokens needed to vote
# If you feel it is secure to do so, put it here, otherwise 
# you will be prompted to input this information at runtime.
email = ""
password = ""
user_id = ""
#
#
# URI settings
#
host = "www.sololearn.com"
uri_base = "https://www.sololearn.com"
#
#
# tapping SL API
#
login_uri = "/user/loginv2"
profile_uri = "/Profile/"
code_voting_uri = '/UserCodes/CodeVoting/'



###################################
## AUXILIARY FUNCTIONS
##
def alert(msg):
    global use_colour
    if use_colour:
        print("\033[1;31m%s\033[0m" % msg)
    else:
        print(msg)

def print_help():
    global use_colour
    if use_colour:
        print("\033[1;37mUsage:\033[0m python3 %s [<ProfileID>]" % sys.argv[0])
        print()
        print("\033[1;37mParameters:\033[0m")
        print("\033[1;33mProfileID\033[0m\tThe unique profile ID of the target to be likestormed\n")
    else:
        print("Usage: python3 %s <ProfileID>" % sys.argv[0])
        print()
        print("Parameters:")
        print("ProfileID\tThe unique profile ID of the target to be likestormed\n")



if len(sys.argv) == 2:
    if sys.argv[1] == 'help':
        print_help()
        sys.exit(0)
    user_id = sys.argv[1]



####################################
## LOGIN logic
## This is necessary to get the cookies necessary to upvote
##
def login_send(email, password):
    creds = {
            "email": email,
            "password": password,
            "subject": "None"
            }
    headers = {
            "Host": "www.sololearn.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json;charset=utf-8",
            "Content-Length": "98",
            "Origin": "https://www.sololearn.com",
            "DNT": "1",
            "Connection": "close",
            "Referer": "https://www.sololearn.com/users/login/"
            }
    res = requests.post(uri_base+login_uri, data=json.dumps(creds), headers=headers, allow_redirects=False)
    if res.status_code == 200:
        cookies = dict_from_cookiejar(res.cookies)
        body = {}
        try:
            body = res.json()
        except:
            alert("Error: Response not in expected JSON format")
            sys.exit(2)
        if not body['success']:
            alert("Login failed with given credentials!")
            sys.exit(1)
        return { "cookies": cookies, "body": body }
    else:
        alert("Login responded with status code %d" % res.status_code)
        sys.exit(3)
    return None


def login_bare():
    global email
    global password
    if not email:
        email = input("email: ")
    password = input("password: ")
    print()
    return login_send(email, password)

def login():
    global email
    global password
    if not email and not password:
        return login_bare()
    else:
        return login_send(email, password)



###################################
## GET Profile Logic
##
def get_profile_send(profileID, cookies={}):
    if not profileID:
        alert("Profile ID is required!")
        sys.exit(5)
    headers = {
            "Host": "www.sololearn.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "close"
            }
    res = requests.get(uri_base+profile_uri+profileID, headers=headers, cookies=cookies, allow_redirects=False)
    if not res.status_code == 200:
        alert("Could not retrieve profile ID %s" % profileID)
        print("Are you sure you have the right number?")
        sys.exit(4)
    else:
        return BeautifulSoup(res.text, features="lxml")

def get_profile(cookies={}):
    global user_id
    if not user_id:
        user_id = input("Enter beneficiary ID: ")
        print()
        if not user_id:
            alert("Profile ID is required!")
            sys.exit(1)
    return get_profile_send(user_id, cookies)

def get_profile_userdata(soup):
    user_profile = soup.find('div', class_='userProfile')
    name = user_profile.div.h1.string
    details = list(user_profile.find('div', class_='detail').find_all('div'))
    level = list(details[0].children)[2]
    xps = details[1].span.string
    return (name.strip(), level.strip(), xps.strip())

def get_profile_codes(soup):
    def extract_code_details(code):
        id = code['data-id']
        details = code.find('div', class_='codeDetails')
        name = details.find('div', class_='codeName').a.string
        votes = details.find('div', class_='actions').p.string
        #active = 'active' in details.find('div', class_='vote').a['class']
        return (id, name, votes)
    user_codes = soup.find('div', id='userCodes').find_all('div', class_='codeContainer')
    code_list = [ extract_code_details(uc) for uc in user_codes ]
    return code_list

def upvote_code(id, name, votes, cookies):
    voting_data = {
            'codeId': id,
            'vote': 1
            }
    headers = {
            "Host": "www.sololearn.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Content-Length": str(len('codeID') + len('vote') + len(id) + 4),
            "Origin": "https://www.sololearn.com",
            "DNT": "1",
            "Connection": "close"
            }
    res = requests.post(uri_base+code_voting_uri, data=voting_data, headers=headers, cookies=cookies)
    sleep(.2)
    if not res.status_code == 200:
        alert("Failed to upvote '%s'" % name)
    else:
        print("Upvoted '%s'" % name)



##################################
## RUN MAIN PROGRAM
##
def print_user_details(user_details):
    print("Flooding '%s' with code upvotes!" % user_details[0])
    print("'%s' is currently level %s, with %s" % user_details)
    print()

def flood_upvotes(code_list, session):
    print("Start flooding....")
    for code_details in code_list:
        upvote_code(*code_details, session['cookies'])


print("Attempt to log in with credentials...")
session = login()

print("Downoading profile...")
soup = get_profile(session['cookies'])
user_details = get_profile_userdata(soup)
print_user_details(user_details)

print("Grabbing code list... ", end='')
code_list = get_profile_codes(soup)
print("done.")
flood_upvotes(code_list, session)
