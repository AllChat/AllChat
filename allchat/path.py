import os

def getPicturePath():
	return os.path.abspath(os.path.join(os.path.dirname(
		os.path.dirname(__file__)),"Data","picture"))