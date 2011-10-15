try:
	import private
except ImportError:
	print "can't do anything until you first define a file called private.py with EMAIL and PASSWORD constants defined in it. sorry!"
	import sys
	sys.exit()

from collections import defaultdict
import datetime

from pyquery import PyQuery as pq
import requests


DISTANCE_TO_PORTLAND = 674

def get_fitbit_homepage(session):
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

	r = session.post('https://www.fitbit.com/login', data=data)
	return pq(r.content)

def previous_days_homepage(homepage, session):
	"""Returns a PyQuery object representing your fitbit dashboard on the day before the day that the passed-in homepage represents."""
	yesterday_url = homepage("#dateNavHeader li a")[0].attrib['href']
	return pq(session.get('http://www.fitbit.com%s' % yesterday_url).content)

def badges_so_far_this_week(homepage, session):
	"""Returns a dict of {badge_name: count} like {'15k': 2, '20k': 1, '10k': 4, '5k': 6}.

	Arguments:
		homepage -- A PyQuery object representing your logged-in fitbit.com homepage.
		session -- a requests.ression() object.
	"""
	possible_badges_in_order = ['5k', '10k', '15k', '20k', '25k', '30k', '35k']

	badge_counts = defaultdict(int)
	for i in range(datetime.date.today().weekday() + 1):
		best_badge_earned = homepage("#activity_daily_badges li.left a.badge")[0].attrib.get('id', '').replace('badge_daily_steps', '')

		if best_badge_earned:
			# if, say, you earned the 15k badge, we'll also increment the counts for the 10k and 5k badges
			for badge in possible_badges_in_order[:possible_badges_in_order.index(best_badge_earned)+1]:
				badge_counts[badge] += 1

		homepage = previous_days_homepage(homepage, session)

	return badge_counts

def weekday_distances(homepage, session):
	"""Returns a list of [miles_walked_on_monday, miles_walked_on_tuesday, ...]"""
	distances = []
	for i in range(datetime.date.today().weekday() + 1):
		distances.append(float(homepage(".distance_traveled span.highlight1")[0].text.strip()))
		homepage = previous_days_homepage(homepage, session)

	return list(reversed(distances))

def main():
	env = {}

	with requests.session() as session:
		homepage = get_fitbit_homepage(session)
		env['badges_this_week'] = badges_so_far_this_week(homepage, session)
		env['weekday_distances'] = weekday_distances(homepage, session)

	goal_words = homepage("#goalScene .details p").text().split() # looks like "['72', '%', 'of', '50.0', 'weekly', 'miles']"
	env['percentage_of_weekly_goal'] = float(goal_words[0])
	env['weekly_goal_in_miles'] = float(goal_words[3])

	env['miles_walked'] = sum(env['weekday_distances'])
	env['miles_remaining'] = env['weekly_goal_in_miles'] - env['miles_walked']


	today = datetime.date.today()
	env['daily_average_so_far'] = env['miles_walked'] / today.weekday()
	env['daily_average_required_for_rest_of_week'] = env['miles_remaining'] / (7 - today.weekday())

	env['best_weekday'] = today - datetime.timedelta(days=today.weekday() - env['weekday_distances'].index(max(env['weekday_distances'])))

	env['lifetime_distance'] = float(homepage(".lifetime .distance span.value")[0].text)
	env['num_times_walked_to_portland'] = env['lifetime_distance'] / DISTANCE_TO_PORTLAND

	from pprint import pprint
	pprint(env)



if __name__ == "__main__":
	main()
