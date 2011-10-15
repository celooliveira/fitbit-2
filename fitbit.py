try:
	import private
except ImportError:
	print "can't do anything until you first define a file called private.py with EMAIL and PASSWORD constants defined in it. sorry!"
	import sys
	sys.exit()

import datetime

from pyquery import PyQuery as pq
import requests

WEEKLY_MILES = 50

data = {
	'email': private.EMAIL,
	'password': private.PASSWORD,
	'login': 'Log In',
	'includeWorkflow': 'false',
	'_sourcePage': 'JyTixiAQ0UPGrJMFkFsv6XbX0f6OV1Ndj1zeGcz7OKzA3gkNXMXGnj27D-H9WXS-',
	'__fp': 'wjVh739tJHNztQ7FkK21Ry2MI7JbqWTf',
	'rememberMe': 'true',
}

r = requests.post('https://www.fitbit.com/login', data=data)
content = pq(r.content)
percentage = int(content("#goalScene .details span").text().split('\r')[0])

today = datetime.date.today()

so_far = percentage / 100.0 * WEEKLY_MILES
remaining = WEEKLY_MILES - so_far

print 'at %s%% of your weekly goal of %s miles' % (percentage, WEEKLY_MILES)
print '%s miles walked this week' % so_far
print '%s miles left to go' % remaining
print '%s miles per day average so far this week' % (so_far / today.weekday())
print '%s miles per day average for the rest of the days in this week required to meet your goal' % (remaining / (7 - today.weekday()))

now = datetime.datetime.now()
seconds_elapsed_this_week = now.second + (60 * now.minute) + (60 * 60 * now.hour) + (60 * 60 * 24 * now.weekday())
percentage_of_week_elapsed = seconds_elapsed_this_week / (7 * 24 * 60 * 60.0) * 100
print percentage_of_week_elapsed
