from bs4 import BeautifulSoup
import requests
import time
import psycopg2
from getlinks import *
from psql_func import *

def convert_pts(txt):
	pts = 0
	negative = 0
	for char in txt:
		if (char == '-'):
			negative = 1
		elif (char.isdigit()):
			pts *= 10
			pts += int(char)
		elif (char.lower() == 'k'):
			pts *= 1000
		else:
			break
	if (negative):
		pts *= -1
	return (pts)

def convert_age(txt):
	age = 0
	for char in txt:
		if (char.isdigit()):
			age *= 0
			age += int(char)
	if (txt.find("year") >= 0):
		age *= 12
	if (txt.find("days") >= 0):
		return (0)
	return (age)

# grabs usernames from a post

def get_usrs(link):
	# stormproxies to get around reddit blocking requests
	# not in use atm...
	# either i'm not using them right or they're not doing shit
	proxies {
		'https' : '108.59.14.203:13010',
		'http' : '108.59.14.203:13010'
	}
	users = []
	while True:
		r = requests.get(link)
		data = r.text
		soup = BeautifulSoup(data, 'html.parser')
		if (soup.title.string != 'Too Many Requests'): # make sure request went through, else keep trying
			break
	for comment in soup.find_all('div', {"data-type" : "comment"}):
		user = {}
		try:
			add = 1
			user['name'] = str(comment['data-author'])
			if users: 	#check for duplicates
				for usr in users:
					if (usr['name'] == user['name']):
						add = 0
			if (add):
				users.append(user)
		except:
			pass
	return (users)

 
# get info from user profile


def get_usr_prof(user):
	user['activity'] = 0
	user['pts'] = 0
	user['age'] = 0
	proxies = {
		'https' : '108.59.14.203:13010',
		'http' : '108.59.14.203:13010'
	}
	link = "https://www.reddit.com/user/" + user['name']
	attempts = 0
	while True and attempts < 20: # attempts just incase infinite loop
		rqsts = 0
		while True and rqsts < 20:
			r = requests.get(link)
			data = r.text
			soup = BeautifulSoup(data, 'html.parser')
			if (soup.title.string != 'Too Many Requests'):
				break
			rqsts += 1
		try:
			age = soup.find('span', {'class' : 'age'}).find('time')
			user['age'] = convert_age(age.text)		# convert to an int
			for post in soup.find_all('div', {"data-type":"comment"}):
				if (post['data-subreddit']):
					if (post['data-subreddit'].find('eth') >= 0 \
						or post['data-subreddit'].find('crypto') >= 0):
						points = post.find('span', {'class' : 'score likes'}).text
						user['pts'] += convert_pts(points)
						user['activity'] += 1
						comment = str(post.find('div', {'class' : 'md'}).text)
		except:
			pass
		try:
			if (soup.find('span', {'class' : 'next-button'})):		# go to next page of user profile
				nxt_btn = soup.find('span', {'class' : 'next-button'})
				link = nxt_btn.find('a')
				link = link['href']
			else:
				break
		except:
			break
		attempts += 1

url = "https://www.reddit.com/r/ethtrader/"
post = get_daily(url)
post += "?limit=500"
users = get_usrs(post)

# connect to psql
try:
	conn = psycopg2.connect("dbname='redditusrs' user='rle' host='localhost' password='pswd'")
except:
	print "Could not connect to database"
	exit()

conn.set_isolation_level(0)
cur = conn.cursor()
db_init(cur)

# add info to db
for user in users:
	get_usr_prof(user)
	if (user['pts'] > 0):
		db_adduser(cur, user)

#close and save db
conn.commit()
cur.close()
conn.close()
