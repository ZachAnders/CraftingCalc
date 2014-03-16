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

def extract_field(row_dict, key, default=None):
	if key in row_dict and row_dict[key] != "":
		if default != None:
			return type(default)(row_dict[key])
		else:
			return row_dict[key]
	return default

if __name__ == "__main__":
	print "Testing"
	tester = DbSession()

