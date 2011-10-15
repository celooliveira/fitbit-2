try:
	import private
except ImportError:
	print "can't do anything until you first define a file called private.py with EMAIL and PASSWORD constants defined in it. sorry!"
	import sys
	sys.exit()

import datetime

from pyquery import PyQuery as pq
import requests

WEEKLY_MILES = 50 # TODO get from page source
DISTANCE_TO_PORTLAND = 674


def get_fitbit_homepage():
	"""Returns a PyQuery object representing your logged-in fitbit.com homepage."""
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
	return pq(r.content)

def main():
	fitbit_homepage = get_fitbit_homepage()

	env = {}
	goal_words = fitbit_homepage("#goalScene .details p").text().split() # "['72', '%', 'of', '50.0', 'weekly', 'miles']"
	env['percentage_of_weekly_goal'] = float(goal_words[0])
	env['weekly_goal_in_miles'] = float(goal_words[3])
	env['miles_walked'] = env['percentage_of_weekly_goal'] / 100.0 * env['weekly_goal_in_miles']
	env['miles_remaining'] = env['weekly_goal_in_miles'] - env['miles_walked']

	today = datetime.date.today()
	env['daily_average_so_far'] = env['miles_walked'] / today.weekday()
	env['daily_average_required_for_rest_of_week'] = env['miles_remaining'] / (7 - today.weekday())

	from pprint import pprint
	pprint(env)



if __name__ == "__main__":
	main()
