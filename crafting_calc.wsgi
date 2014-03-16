import sys, site, os
sys.path.insert(0, '/var/www/calc/craftingcalc/CraftingCalc')
site.addsitedir("/var/www/calc/craftingcalc/lib/python2.7/site-packages")
os.environ["PRODUCTION"] = str(True)
from Application import app as application
