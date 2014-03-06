from flask import session, render_template
from functools import wraps

def is_valid_user(some_user, timestamp):
	"""Given a user, is this a valid user?"""
	if some_user == "admin":
		return True

def requires_session(some_route):
	# Flask requires that decorators are implemented utilizing functools
	@wraps(some_route)
	def protected(*args, **kwargs):
		if valid_session():
			return some_route(*args, **kwargs)
		else:
			return render_template("error.html")
	return protected

def valid_session():
	"""Returns True only if there is currently a valid username in the session"""
	if "username" in session:
		#TODO: Add timestamp
		if is_valid_user(session["username"], 0):
			return True
	return False

def has_valid_credentials(user, passw):
	if user == "admin" and passw == "admin":
		return True
	return False
