#!/usr/bin/env python
import os
import math
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from AppAuth import has_valid_credentials, requires_session, create_user, get_user
from DbSession import DbSession
from CalcSchema import Wright, User, Job
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("login.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		user, pw = request.form["username"], request.form["password"]
		if has_valid_credentials(user, pw):
			session["username"] = user
			return redirect(url_for("calc"))
		return render_template("login.html", login_style="active", error="Incorrect Username or Password! Please double check them and try again.")
	else:
		return render_template("login.html", login_style="active")

@app.route("/create_acct", methods=['GET', 'POST'])
def create_acct():
	if request.method == "POST":
		username, pw1, pw2 = request.form["username"], request.form["password1"], request.form["password2"]
		if pw1 != pw2:
			return render_template("login.html", create_style="active", error="Passwords do not match. Please try again.")

		sess = DbSession().get_session()
		new_user = create_user(User, username, pw1)
		new_user.XpPool = 0
		new_user.GoldPool = 0
		sess.add(new_user)
		sess.commit()
		
		flash("Account %s created!" % (username))
		return redirect(url_for("login"))
		
	else:
		return render_template("create_acct.html", create_style="active")

@app.route("/logout")
def logout():
	if "username" in session:
		del session["username"]
	flash("You have been logged out.")
	return redirect(url_for("login"))

@app.route("/calc")
@requires_session
def calc():
	sess = DbSession().get_session()
	user = get_user(sess, session["username"])
	sess.commit()
	#wrights = sess.query(Wright).filter(Wright.OwnerId == User.Id).all()
	#jobs = sess.query(Job).filter(Job.OwnerId == User.Id).all()
	if "next_tab" in session:
		current_tab = session["next_tab"]
		del session["next_tab"]
	else:
		current_tab = 0
	return render_template("calc.html", user=user, current_tab=current_tab)

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

@app.route("/del_wright", methods=['POST'])
@requires_session
def del_wright():
	sess = DbSession().get_session()
	wright = sess.query(Wright).filter(Wright.Id == request.form["id"]).first()
	sess.delete(wright)
	sess.commit()
	return jsonify({"status":1})

@app.route("/modify_resources", methods=['POST'])
@requires_session
def modify_resources():
	sess = DbSession().get_session()
	user = get_user(sess, session["username"])
	op = request.form["action"]
	if op == "add_gold":
		user.GoldPool += int(request.form["value"])
		sess.commit()
		return jsonify({"status":1, "value":str(user.GoldPool)})
	elif op == "add_exp":
		user.XpPool += int(request.form["value"])
		sess.commit()
		return jsonify({"status":1, "value":str(user.XpPool)})
	else:
		return jsonify({"status":0})

@app.route("/add_job", methods=['POST'])
@requires_session
def add_job():
	sess = DbSession().get_session()
	user = get_user(sess, session["username"])
	new_job = Job()
	new_job.OwnerId = user.Id
	
	post = request.form
	try:
		new_job.Name = post["name"]
		base_price = int(post["base_price"])
		new_job.GoldCost = (base_price/2)*.75
		new_job.XpCost = (base_price/25)*.75
		new_job.TimeCost = math.ceil((base_price/1000)*.75)
		new_job.TimeStart = new_job.TimeCost

		if "mage_armor" in post:
			if int(post["mage_armor"]):
				new_job.XpCost /= 2
		if "gp_multi" in post:
			new_job.GoldCost *= int(post["gp_multi"])
		if "notes" in post:
			new_job.Notes = post["notes"]
		if "priority" in post:
			new_job.Priority = int(post["priority"])
		if "exp_adjust" in post and post["exp_adjust"] != "":
			new_job.XpCost += int(post["exp_adjust"])
		if "gold_adjust" in post and post["gold_adjust"] != "":
			new_job.GoldCost = min(0, new_job.GoldCost + int(post["gold_adjust"]))
	except ValueError:
		return jsonify({"status":0, "error":"Double check fields. Integers only please."}) 

	if user.GoldPool < new_job.GoldCost:
		return jsonify({"status":0, "error":"Insufficient Gold. Gold remaining: %d. Needed: %d." % (user.GoldPool, new_job.GoldCost)}) 
	if user.XpPool < new_job.XpCost:
		return jsonify({"status":0, "error":"Insufficient Experience. Experience remaining: %d. Needed: %d." % (user.XpPool, new_job.XpCost)}) 

	user.GoldPool -= new_job.GoldCost
	user.XpPool -= new_job.XpCost

	sess.add(new_job)
	sess.commit()
	session["next_tab"] = 2
	return jsonify({"status":1})

@app.route("/del_job", methods=['POST'])
@requires_session
def rm_job():
	sess = DbSession().get_session()
	user = get_user(sess, session["username"])
	job = sess.query(Job).filter(Job.Id == request.form["id"]).first()
	if job.TimeCost != 0:
		user.GoldPool += job.GoldCost
		user.XpPool += job.XpCost
	sess.delete(job)
	sess.commit()
	return jsonify({"status":1})

@app.route("/pass_time", methods=['POST'])
@requires_session
def pass_time():
	sess = DbSession().get_session()
	user = get_user(sess, session["username"])

	time_to_pass = int(request.form["value"])
	while True:
		job_completed = False
		free_wrights = [wright for wright in user.wrights if not wright.currentJob]
		available_jobs = [job for job in user.jobs if not job.wright and job.TimeCost != 0]
		available_jobs = sorted(available_jobs, key=lambda job: -job.Priority)
		if len(free_wrights) == len(user.wrights) and len(available_jobs) == 0:
			break
		for wright in free_wrights:
			if len(available_jobs) > 0:
				wright.currentJob = available_jobs.pop(0)
				sess.commit()
		print free_wrights, available_jobs

		time_step = min([job.TimeCost for job in user.jobs if job.wright] + [time_to_pass])
		time_to_pass -= time_step
		print time_step
		print [job.TimeCost for job in user.jobs if job.wright]

		for wright in user.wrights:
			if wright.currentJob:
				wright.currentJob.TimeCost -= time_step
				if wright.currentJob.TimeCost == 0:
					wright.currentJob = None
					job_completed = True
		sess.commit()
		if time_to_pass <= 0 and not job_completed:
			break
	session["next_tab"] = 0
	return redirect(url_for("calc"))

app.secret_key = os.urandom(128)

if __name__ == "__main__":
	app.debug = True
	if app.debug:
		app.secret_key = '\xe5\x1e\xe8\xc7h\xccr\x9c7\xee|dN\x85\x8c{-4<\xa5\xe5\x03\xc7?\x16\xc3\x181+\xab\xf3q'
	app.run()
