import sqlalchemy
import sqlalchemy.orm

class DbSession():
	def __init__(self):
		self.eng = sqlalchemy.create_engine("mysql://root:usemysql@localhost/craftingcalc")
		self.session_maker = sqlalchemy.orm.sessionmaker(bind=self.eng)
		self.current_session = self.session_maker()
	def get_session(self):
		return self.current_session
	def build_tables(self, base):
		base.metadata.create_all(self.eng)

if __name__ == "__main__":
	print "Testing"
	tester = DbSession()

