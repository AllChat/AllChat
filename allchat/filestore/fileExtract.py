# --*-- coding:utf-8 --*--
import os
from encrypt import Encryptor

class FileExtractor(object):
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
    def getChatRecord(self, startTime, endTime, option):
        ''' get the chat record of required users in the specific time duration.
            option(dict) contains user/group information, 'type'=user/group;
            in case of user, there shall include 'chatFrom'=... and 'chatTo'=...
            in case of group, there shall include 'groupName'=... and 'userName'
            if no files can be found according to the params, returns None
            startTime and endTime format = '%Y%m%d', such as 20140522 etc.
        '''
        if option['type'] == 'user':
            chatFrom = option['chatFrom']
            chatTo = option['chatTo']
            msg_dir = os.path.abspath(self.current_dir + '/../../Data/messages')
            chatPath = os.path.join(msg_dir,chatFrom,chatTo)
            if not os.path.exists(chatPath):
                return 'No history message is found.'
            else:
                result_list = []
                for directory in os.listdir(chatPath):
                    if self.dateLaterThan(directory,startTime) and \
                       self.dateLaterThan(endTime,directory):
                        msg_list = self.getRecordInFolder(os.path.join(chatPath,directory))
                        result_list.extend(msg_list)
                return result_list
        elif option['type'] == 'group':
            groupName = option['groupName']
            userName = option['userName']
            ## validate the user whether belongs to the group
            msg_dir = os.path.abspath(self.current_dir + '/../../Data/Group messages')
            chatPath = os.path.join(msg_dir,groupName)
            if not os.path.exists(chatPath):
                return 'No history message is found.'
            else:
                result_list = []
                for dirs in os.listdir(chatPath):
                    if self.dateLaterThan(dirs,startTime) and \
                       self.dateLaterThan(endTime,dirs):
                        msg_list = self.getRecordInFolder(os.path.join(chatPath,dirs))
                        result_list.extend(msg_list)
                return result_list

    def dateLaterThan(self,Day,ComparedTo):
        if Day[0:4]>ComparedTo[0:4] or \
        (Day[0:4]==ComparedTo[0:4] and Day[4:6]>ComparedTo[4:6]) or \
        (Day[0:6]==ComparedTo[0:6] and Day[6:]>=ComparedTo[6:]):
            return True
        else:
            return False

    def getRecordInFolder(self,path):
        msg_list = []
        for root,subpathList,fileList in os.walk(path):
            for file_name in fileList:
                if file_name.endswith('.bin'):
                    fileHandler = open(os.path.join(root,file_name),'rb')
                    string = fileHandler.read()
                    encryptor = Encryptor()
                    content = encryptor.DecryptStr(string)
                    temp_msg_list = []
                    for msg in content.split('&*'):
                        (speaker,time_content) = msg.split('&:')
                        (time,msg_content) = time_content.split('\t')
                        temp_msg_list.append((speaker,time,msg_content))
                    msg_list.extend(temp_msg_list)
        return msg_list
