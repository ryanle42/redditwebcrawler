from bs4 import BeautifulSoup
import requests
import time

def get_links(url):	
	links = []
	while True:
		r = requests.get(url)
		data = r.text
		soup = BeautifulSoup(data, 'html.parser')
		if (soup.title.string != 'Too Many Requests'):
			break
	for tag in soup.find_all('ul', {'class' : 'flat-list buttons'}):
		try:
			for link in tag.find_all('a', {'class' : 'bylink comments may-blank'}):
				links.append(link['href'])
		except:
			pass
	return (links)

def get_daily(url):
	for link in get_links(url):
		if (link.find('daily') >= 0 and link.find('general') >= 0):
			return (link)