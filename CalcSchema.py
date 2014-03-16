#!/usr/bin/python

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from DbSession import DbSession, extract_field
import math

Base = declarative_base()

class Wright(Base):
	__tablename__ = "Wright"
	Id = Column(Integer, primary_key=True)
	OwnerId = Column(Integer, ForeignKey("User.Id"))
	Name = Column(String(64))
	currentJob = relationship("Job", uselist=False, backref="Wright")
	owner = relationship("User", foreign_keys="Wright.OwnerId")

class Job(Base):
	__tablename__ = "Job"
	Id = Column(Integer, primary_key=True)
	OwnerId = Column(Integer, ForeignKey("User.Id"))
	WrightId = Column(Integer, ForeignKey("Wright.Id"))
	Name = Column(String(64))
	Priority = Column(Integer)
	GoldCost = Column(Integer)
	TimeCost = Column(Integer)
	TimeStart = Column(Integer)
	XpCost = Column(Integer)
	Notes = Column(Text)
	owner = relationship("User", foreign_keys="Job.OwnerId")
	wright = relationship("Wright", foreign_keys="Job.WrightId")

	def apply_mage_armor(self):
		self.XpCost /= 2.0

	def set_base_price(self, val):
		val = int(val)
		self.GoldCost = math.ceil((val/2.0)*.75)
		self.XpCost = math.ceil((val/25.0)*.75)
		self.TimeCost = max(1, math.ceil((val/1000.0)*.75))
		self.TimeStart = self.TimeCost

	def populate(self, j_dict):
		try:
			self.Name = j_dict["name"]
			self.set_base_price(j_dict["base_price"])
			#base_price = int(j_dict["base_price"])
			#self.Priority = 1

			if extract_field(j_dict, "mage_armor"):
				self.apply_mage_armor()
			self.GoldCost *= extract_field(j_dict, 'gp_multi', default=1.0)
			self.Notes = extract_field(j_dict, 'notes', default="")
			self.Priority = extract_field(j_dict, 'priority', default=1)
			self.XpCost += extract_field(j_dict, 'exp_adjust', default=0)
			self.GoldCost += extract_field(j_dict, 'gold_adjust', default=0)

			#if "mage_armor" in j_dict and int(j_dict["mage_armor"]):
			#	self.XpCost /= 2.0
			#if "gp_multi" in j_dict:
			#	self.GoldCost *= float(j_dict["gp_multi"])
			#if "notes" in j_dict:
			#	self.Notes = j_dict["notes"]
			#if "priority" in j_dict and j_dict["priority"] != "":
			#	self.Priority = int(j_dict["priority"])
			#if "exp_adjust" in j_dict and j_dict["exp_adjust"] != "":
			#	self.XpCost += int(j_dict["exp_adjust"])
			#if "gold_adjust" in j_dict and j_dict["gold_adjust"] != "":
			#	self.GoldCost = max(0, self.GoldCost + int(j_dict["gold_adjust"]))
			#if "qty_adj" in j_dict and j_dict["qty_adj"] == "":
			#	job_quantity = int(j_dict["qty_adj"])
		except ValueError:
			return False
		return True 

	def get_completion_percentage(self):
		if not self.TimeStart:
			return 100
		percent = (self.TimeCost*100)/self.TimeStart
		return int(100 - percent)

	def clone(self):
		job_clone = Job()
		job_clone.OwnerId = self.OwnerId
		job_clone.WrightId = self.WrightId
		job_clone.Name = self.Name
		job_clone.Priority = self.Priority
		job_clone.GoldCost = self.GoldCost
		job_clone.TimeCost = self.TimeCost
		job_clone.TimeStart = self.TimeStart
		job_clone.XpCost = self.XpCost
		job_clone.Notes = self.Notes
		return job_clone

class User(Base):
	__tablename__ = "User"
	Id = Column(Integer, primary_key=True)
	Username = Column(String(32), index=True)
	Password = Column(Text)
	Timestamp = Column(Integer)
	XpPool = Column(Integer)
	GoldPool = Column(Integer)
	CurrentTimeVal = Column(Integer)
	wrights = relationship("Wright", backref="User")
	jobs = relationship("Job", backref="User")

	def num_jobs_completed(self):
		return sum([1 for job in self.jobs if job.TimeCost == 0])

if __name__ == "__main__":
	sess = DbSession()
	sess.build_tables(Base)
