import os

def get_project_root():
	return os.path.dirname(os.path.dirname(__file__))

def get_single_msg_dir():
	return os.path.join(get_project_root(),"Data","single_messages")

def get_group_msg_dir():
	return os.path.join(get_project_root(),"Data","group_messages")

def get_picture_dir():
	return os.path.join(get_project_root(),"Data","picture")