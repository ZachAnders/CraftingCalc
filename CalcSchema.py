#!/usr/bin/python

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from DbSession import DbSession

Base = declarative_base()

class Wright(Base):
	Id = Column(Integer, primary_key=True)
	OwnerId = Column(Integer, ForeignKey("User.Id"))
	Name = Column(String)
	JobId = Column(Integer, ForeignKey("Job.Id"))
	currentJob = relationship("Job", foreign_keys="Wright.JobId")

class Job(Base):
	Id = Column(Integer, primary_key=True)
	OwnerId = Column(Integer, ForeignKey("User.Id"))
	WrightId = Column(Integer, ForeignKey("Wright.Id"))
	Name = Column(String)
	GoldCost = Column(Integer)
	TimeCost = Column(Integer)
	XpCost = Column(Integer)
	Notes = Column(String)
	owner = relationship("User", foreign_keys="Job.OwnerId")
	wright = relationship("Wright", foreign_keys="Job.WrightId")

class User(Base):
	Id = Column(Integer, primary_key=True)
	Username = Column(String)
	Password = Column(String)
	PwSalt = Column(String)
	XpPool = Column(Integer)
	GoldPool = Column(Integer)
	wrights = relationship("Wright", uselist=False, backref="User")
	jobs = relationship("Job", uselist=False, backref="User")

if __name__ == "__main__":
	sess = DbSession()
	sess.build_tables(Base)
