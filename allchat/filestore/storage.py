# -*- coding:utf-8 -*-
import os
import time
import hashlib
from multiprocessing import Process, Queue
from encrypt import Encryptor
from allchat.path import get_single_msg_dir, get_group_msg_dir, get_picture_dir, get_project_root

class MessageSaver(object):
    def __init__(self):
        self._single_message_queue = Queue()
        self._group_message_queue = Queue()
        self._get_config()
        self._terminator = "\nquit\n"
        self._single_message_proc = None
        self._group_message_proc = None

    def _init_config(self, conf_path):
        if not os.path.exists(os.path.dirname(conf_path)):
            os.makedirs(os.path.dirname(conf_path))
        with open(conf_path,"wb") as conf:
            _encrypt_key = int(os.urandom(16).encode("hex"),16)
            encrypt_key = " ".join(("encrypt_key",str(_encrypt_key)))+";"
            conf.write(encrypt_key)

    def _get_config(self):
        root = get_project_root()
        conf_path = os.path.join(root, "conf", "blizzard.conf")
        if not os.path.exists(conf_path):
            self._init_config(conf_path)
        with open(conf_path,"rb") as conf:
            config_dict = dict(tuple(line.split(";")[0].split(" "))
                               for line in conf)
        self._encrypt_key = int(config_dict.get("encrypt_key"))

    def __stop_writing(self):
        if self._single_message_proc:
            self._single_message_queue.put(self._terminator)
            self._single_message_proc.join()
        if self._group_message_proc:
            self._group_message_queue.put(self._terminator)
            self._group_message_proc.join()

    def saveSingleMsg(self, sender, receiver, msg):
        if sender and receiver and isinstance(msg, list) and msg[0] and msg[1]:
            users = "&&".join(set([sender,receiver]))
            self._single_message_queue.put((sender,users,msg))
            if not self._single_message_proc:
                self._single_message_proc = Process(target=_write_message, args=(self._single_message_queue,
                                                                self._terminator,
                                                                self._encrypt_key,
                                                                get_single_msg_dir(),))
                self._single_message_proc.start()
            return True
        else:
            return False

    def saveGroupMsg(self, sender, group_id, msg):
        if sender and group_id and isinstance(msg, list) and msg[0] and msg[1]:
            self._group_message_queue.put((sender,str(group_id),msg))
            if not self._group_message_proc:
                self._group_message_proc = Process(target=_write_message, args=(self._group_message_queue,
                                                                self._terminator,
                                                                self._encrypt_key,
                                                                get_group_msg_dir(),))
                self._group_message_proc.start()
            return True
        else:
            return False

    def savePicture(self, content, format_):
        if content and format_:
            md5 = hashlib.md5()
            md5.update(content)
            pic_name = md5.hexdigest()
            path = os.path.join(get_picture_dir(),pic_name+"."+format_)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with open(path,"wb") as output:
                output.write(content)
            return pic_name+"."+format_
        else:
            return False

def _write_message(queue, terminator, encrypt_key, root_dir):
    encryptor = Encryptor(encrypt_key)
    while True:
        message = queue.get()
        if message == terminator:
            break
        sender, sub_dir, msg = message
        date = time.strftime("%Y-%m-%d", time.localtime())
        year, month, day = date.split("-")
        directory = os.path.join(root_dir, sub_dir, year, month)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = os.path.join(directory, day+".bin")
        msg_sep = "\t\t"
        content = msg_sep.join((sender,msg[0],msg[1]))
        with open(file_name,"a+") as output:
            output.write(encryptor.EncryptStr(content))
            output.write(os.linesep)
