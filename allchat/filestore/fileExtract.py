# --*-- coding:utf-8 --*--
import os,time,datetime
from encrypt import Encryptor
from allchat.filestore import saver

class FileExtractor(object):
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
    def getChatRecord(self, startTime, offset, reverse, option):
        ''' get the chat record of required users start from specific date.
            option(dict) contains user/group information, 'type'=user/group;
            in case of user, there shall include 'chatFrom'=... and 'chatTo'=...
            in case of group, there shall include 'groupName'=... and 'userName'
            if no files can be found according to the params, returns None
            startTime format = '%Y%m%d', such as 20140522 etc.
            offset indict the index of the first msg to response from the given
            date, 0 base indexed, if the given date has no msg, search from the
            following days.
            reverse indict whether the search direction is inverse or sequential,
            value is either 'true' or 'false'.
        '''
        if option['type'] == 'user':
            chatFrom = option['chatFrom']
            chatTo = option['chatTo']
            msg_dir = os.path.abspath(self.current_dir + '/../../Data/messages')
            chatPath = os.path.join(msg_dir,chatFrom,chatTo)
        elif option['type'] == 'group':
            groupName = option['groupName']
            userName = option['userName']
            msg_dir = os.path.abspath(self.current_dir + '/../../Data/Group messages')
            chatPath = os.path.join(msg_dir,groupName)
        if not os.path.exists(chatPath):
            return 'No history message is found.'
        else:
            result_list = []
            response_segment_size = 30
            if reverse is 'true':
                if startTime == time.strftime("%Y%m%d",time.localtime()):
                    result_list.extend(self.getRecordFromBuffer(offset,reverse,option,response_segment_size))
                    if len(result_list)>=response_segment_size:
                        return
                for dirs in os.listdir(chatPath)[::-1]:
                    if self.strToDate(dirs)<=self.strToDate(startTime):
                        offset, msg_list = self.getRecordInFolder(os.path.join(chatPath,dirs),offset,
                            response_segment_size-len(result_list),reverse)
                        result_list.extend(msg_list)
                        if len(result_list)>=response_segment_size:
                            break
            ## update by dongzai on 2014-07-28
            ## add the buffered msgs to chat records if now is in the search date range
            # current_date = time.strftime("%Y%m%d",time.localtime())
            # if self.strToDate(endTime)>=self.strToDate(current_date):
            return result_list

    def getRecordFromBuffer(self,offset,reverse,option,response_segment_size):
        msg_list = list()
        msgBuffer = saver.getMsgBuffer()
        if 'chatFrom' in option:
            chatFrom = option['chatFrom']
            chatTo = option['chatTo']
            if '::'.join([chatFrom,chatTo]) in msgBuffer:
                msg_list = [msg.split('&:') for msg in msgBuffer['::'.join([chatFrom,chatTo])]]
            if '::'.join([chatTo,chatFrom]) in msgBuffer:
                msg_list = [msg.split('&:') for msg in msgBuffer['::'.join([chatTo,chatFrom])]]
        else:
            if option['groupName'] in msgBuffer:
                msg_list = [msg.split('&:') for msg in msgBuffer[option['groupName']]]
        if reverse is 'true':
            msg_list = msg_list[::-1]
        ## offset from the start
        return msg_list[:min(response_segment_size,len(msg_list))]

    def strToDate(self,Day):
        return datetime.datetime(int(Day[:4]),int(Day[4:6]),int(Day[6:]))

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
                        temp_msg_list.append(msg.split('&:'))
                    msg_list.extend(temp_msg_list)
        return msg_list
