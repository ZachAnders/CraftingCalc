#!/usr/bin/env python
import json, os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from AppAuth import has_valid_credentials, requires_session, create_user, get_user
from DbSession import DbSession
from CalcSchema import Wright, Job, User
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("login.html")

@app.route("/calc")
@requires_session
def calc():
	sess = DbSession().get_session()
	user = get_user(sess, session["username"])
	wrights = sess.query(Wright).filter(Wright.OwnerId == User.Id).all()
	if "next_tab" in session:
		current_tab = session["next_tab"]
		del session["next_tab"]
	else:
		current_tab = 2

	return render_template("calc.html", user=user, wrights=wrights, current_tab=current_tab)

@app.route("/add_wright", methods=['POST'])
@requires_session
def add_wright():
	sess = DbSession().get_session()
	new_wright = Wright()
	#user = sess.query(User).filter(User.Username == session["username"])
	user = get_user(sess, session["username"])
	new_wright.OwnerId = user.Id
	new_wright.Name = request.form["wright_name"]
	sess.add(new_wright)

	sess.commit()
	session["next_tab"] = 2
	return redirect(url_for("calc"))

@app.route("/rm_wright", methods=['POST'])
@requires_session
def rm_wright():
	sess = DbSession().get_session()
	wright = sess.query(Wright).filter(Wright.Id == request.form["wright_id"]).first()
	sess.delete(wright)
	sess.commit()
	return '{"status":"success"}'


@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		user, pw = request.form["username"], request.form["password"]
		if has_valid_credentials(user, pw):
			session["username"] = user
			return redirect(url_for("calc"))
		return render_template("login.html", error="Incorrect Username or Password! Please double check them and try again.")
	else:
		return render_template("login.html")

@app.route("/create_acct", methods=['GET', 'POST'])
def create_acct():
	if request.method == "POST":
		username, pw1, pw2 = request.form["username"], request.form["password1"], request.form["password2"]
		if pw1 != pw2:
			return render_template("login.html", error="Passwords do not match. Please try again.")

		sess = DbSession().get_session()
		new_user = create_user(User, username, pw1)
		new_user.XpPool = 0
		new_user.GoldPool = 0
		sess.add(new_user)
		sess.commit()
		
		flash("Account %s created!" % (username))
		return redirect(url_for("login"))
		
	else:
		return render_template("create_acct.html")

@app.route("/logout")
def logout():
	if "username" in session:
		del session["username"]
	flash("You have been logged out.")
	return redirect(url_for("login"))

if __name__ == "__main__":
	app.debug = True
	if app.debug:
		app.secret_key = '\xe5\x1e\xe8\xc7h\xccr\x9c7\xee|dN\x85\x8c{-4<\xa5\xe5\x03\xc7?\x16\xc3\x181+\xab\xf3q'
	else:
		app.secret_key = os.urandom(128)
	app.run()

