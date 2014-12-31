
## ========================
## This script scrapes your personal Facebook wall for the past year (or more),
## in order for anyone to be able to compare what appeared in their Year in Review
## to the actual data from the year of trace data.
## This script was created because the "Download Data" feature does not provide
## any statistics about likes or comments on your contributed posts. 
## 
## This script assumes a PostgreSQL database installation prior to running.
## It will collect metadata about every post that appears on your Facebook wall.
## To compare to the Year in Review, be sure to filter out things you didn't post yourself.
## Ie., select * from DB_TABLE where post_story is NULL and post_link = 'Your Name'
## ========================

import facebook
import urllib2
import datetime
import time
import psycopg2
from config import *

conn_string = "host='localhost' dbname="+DATABASE_NAME+" user="+DB_USERNAME+" password="+DB_PASSWORD
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

## this token can be found here: https://developers.facebook.com/tools/explorer?method=GET&path=me%2Ffeed&version=v2.2
## click Get Access Token and select ALL of the options, including in the Extended Permissions section
## be aware that this token can expire in a few hours after generation
token = FB_TOKEN 

graph = facebook.GraphAPI(token)

until_num_storage = [1419065508] #this is an arbitrary timestamp for a starting threshold for the pagination

created_date = time.strptime('2014-12-31', '%Y-%m-%d')
print created_date
# print created_date.strftime('%Y-%m-%d')

def grab_posts(until_num):
	profile = graph.get_object("me/feed", limit=25, until=until_num)

	next_set_url = profile['paging']['next']
	next_set_url = next_set_url.split("&until=")
	next_set_url = next_set_url[1]
	until_num = next_set_url
	until_num_storage.append(until_num)

	for x in profile['data']:
		print "---------------------------"
		print x
		print "---------------------------"
		post_type = x['type']
		print post_type
		try: post_story = x['story']
		except: post_story = None
		print post_story
		post_from = x['from']['name']
		print post_from
		try: 
			for y in x['actions']:
				post_link = y['link']
		except: post_link = None
		print post_link
		created_time = x['created_time']
		created_time = created_time.split("T")[0]
		created_date = time.strptime(created_time, '%Y-%m-%d')
		print created_time
		# print created_date.strftime('%Y-%m-%d')
		# if post_type == "photo":
		# 	print "**********"
		# 	print x
		# 	print "**********"
		post_id = x['id']
		print post_id
		try: 
			post_message = x['message']
		except:
			post_message = None
		print post_message
		likes = graph.get_object(str(post_id)+"/likes", limit=100)
		num_likes = len(likes['data'])
		# print "---------------------------"
		# print likes
		# print "---------------------------"
		print num_likes
		comments = graph.get_object(str(post_id)+"/comments", limit=100)
		num_comments = len(comments['data'])
		# print "==========================="
		# print comments
		# print "==========================="
		print num_comments
		print ""

		cursor.execute('INSERT INTO '+DB_TABLE+' (post_type, post_story, post_from, post_link, created_time, post_id, post_message, num_likes, num_comments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (post_type, post_story, post_link, post_from, created_time, post_id, post_message, num_likes, num_comments))
		conn.commit()

while created_date > time.strptime('2013-12-31', '%Y-%m-%d'): #for some reason this doesn't actually stop it; gotta fix later
	grab_posts(until_num_storage[-1])