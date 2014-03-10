#!/usr/bin/python

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from DbSession import DbSession

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
	
	def get_completion_percentage(self):
		if not self.TimeStart:
			return 100
		percent = (self.TimeCost*100)/self.TimeStart
		return int(100 - percent)

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
