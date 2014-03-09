import sys, site
sys.path.insert(0, '/var/www/calc/craftingcalc/CraftingCalc')
site.addsitedir("/var/www/calc/craftingcalc/lib/python2.7/site-packages")
from Application import app as application
