#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<alen-alex>
  Purpose: provide a message content retrieval interface to web server,
           retrieve from /data directory
  Created: 2014/11/4
"""

import os
import json
from .encrypt import Encryptor
from allchat.path import get_project_root

#----------------------------------------------------------------------
def getMessages(directory, date):
    """retrieve the messages stored in files
       param: directory: the place where files should be searched from;
       param: date: the date of files to retrieve, format by "yyyy-mm-dd";
    """
    try:
        query_year, query_month, query_day = date.split("-")
    except ValueError:
        return ("Wrong date format", 404)
    file_ = os.path.join(directory,query_year,query_month,query_day+".bin")
    if not os.path.exists(file_):
        return ("File does not exist", 404)
    messages = _read_file(file_)
    return json.JSONEncoder().encode(messages)

#----------------------------------------------------------------------
def _read_file(file_path):
    """"""
    key,IV = _get_encrypt_key()
    encryptor = Encryptor(key,IV)
    messages = list()
    with open(file_path,"rb") as output:
        sep = b"\0\1\2\3\4"*2
        lines = output.read().rstrip(sep)
        for line in lines.split(sep):
            try:
                line = encryptor.DecryptStr(line)
                messages.append(line.split("\t\t"))
            except Exception as e:
                print(e)
    return messages

#----------------------------------------------------------------------
def _get_encrypt_key():
    """"""
    root = get_project_root()
    conf_path = os.path.join(root, "conf", "blizzard.conf")
    if not os.path.exists(conf_path):
        raise ValueError("Invalid config file path.")
    with open(conf_path,"rb") as conf:
        configs = conf.read()
        config_dict = dict(tuple(line.split(b"="))
                           for line in configs.split(b"\n"))
    return (config_dict.get(b"encrypt_key"),
            config_dict.get(b"IV"))

def getDates(path):
    result = list()
    if os.path.exists(path):
        for year in os.listdir(path):
            for month in os.listdir(os.path.join(path,year)):
                for file_name in os.listdir(os.path.join(path,year,month)):
                    if file_name.endswith(".bin"):
                        result.append("-".join(
                            (year,month,file_name.rstrip(".bin"))
                            ))
    else:
        return ("No records found", 404)
    return json.JSONEncoder().encode(result)
