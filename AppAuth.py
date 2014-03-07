from flask import session, render_template
from DbSession import DbSession
from CalcSchema import User
from functools import wraps
from passlib.apps import custom_app_context as passlib_ctx
import time

#def is_valid_user(some_user, timestamp):
#	"""Given a user, is this a valid user?"""
#	if some_user == "admin":
#		return True

def get_user(sess, some_user):
	#sess = DbSession().get_session()
	res = sess.query(User).filter(User.Username == some_user).all()
	if len(res) != 1:
		return None
	return res[0]

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
	db_sess = DbSession().get_session()
	if "username" in session:
		user = get_user(db_sess, session["username"])
		if user and user.Timestamp+(60*60*24*7) > time.time():
			return True
	return False

def has_valid_credentials(username, passw):
	db_sess = DbSession().get_session()

	user = get_user(db_sess, username)
	if passlib_ctx.verify(passw, user.Password):
		user.Timestamp = time.time()
		db_sess.commit()
		return True
	return False

def create_user(user_class, username, passw):
	new_user = user_class()
	new_user.Username = username
	new_user.Password = passlib_ctx.encrypt(passw)
	return new_user

