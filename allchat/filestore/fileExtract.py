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
            offset is the last msg that has been received, response msgs should
            start from the next msg of the offset, set to '' to indict no offset.
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
            response_segment_size = 20
            if reverse:
                if startTime == time.strftime("%Y%m%d",time.localtime()):
                    result_list.extend(self.getRecordFromBuffer(offset,reverse,option,response_segment_size))
                    if len(result_list)>=response_segment_size:
                        return [startTime,result_list[:response_segment_size]]
                    if result_list:
                        offset = ''
                for dirs in os.listdir(chatPath)[::-1]:
                    if self.strToDate(dirs)<=self.strToDate(startTime):
                        msg_list = self.getRecordInFolder(os.path.join(chatPath,dirs),offset,
                            response_segment_size-len(result_list),reverse)
                        result_list.extend(msg_list)
                        if result_list:
                            offset = ''
                        if len(result_list)>=response_segment_size:
                            return [dirs,result_list[:response_segment_size]]
                return ['',result_list[:response_segment_size]]
            else:
                for dirs in os.listdir(chatPath):
                    if self.strToDate(dirs)>=self.strToDate(startTime):
                        msg_list = self.getRecordInFolder(os.path.join(chatPath,dirs),offset,
                            response_segment_size-len(result_list),reverse)
                        result_list.extend(msg_list)
                        if result_list:
                            offset = ''
                        if len(result_list)>=response_segment_size:
                            return [dirs,result_list[:response_segment_size]]
                temp_list = self.getRecordFromBuffer(offset,reverse,option,response_segment_size-len(result_list))
                result_list.extend(temp_list)
                return [startTime, result_list[:response_segment_size]]

    def getRecordFromBuffer(self,offset,reverse,option,segment_size):
        msg_list = list()
        msgBuffer = saver.getMsgBuffer()
        if 'chatFrom' in option:
            chatFrom = option['chatFrom']
            chatTo = option['chatTo']
            if '::'.join([chatFrom,chatTo]) in msgBuffer:
                msg_list = msgBuffer['::'.join([chatFrom,chatTo])]
            if '::'.join([chatTo,chatFrom]) in msgBuffer:
                msg_list = msgBuffer['::'.join([chatTo,chatFrom])]
        else:
            if option['groupName'] in msgBuffer:
                msg_list = msgBuffer[option['groupName']]
        if reverse:
            msg_list = msg_list[::-1]
        ## offset from the start
        if not offset:
            return msg_list[:min(segment_size,len(msg_list))]
        elif offset not in msg_list:
            return []
        else:
            index = msg_list.index(offset)
            return msg_list[index+1:]

    def strToDate(self,Day):
        return datetime.datetime(int(Day[:4]),int(Day[4:6]),int(Day[6:]))

    def getRecordInFolder(self,path,offset,segment_size,reverse):
        msg_list = []
        file_list = []
        for root,subpathList,fileList in os.walk(path):
            for file_name in fileList:
                if file_name.endswith('.bin'):
                    file_list.append(os.path.join(root,file_name))
        if reverse:
            file_list = file_list[::-1]
        for path in file_list:
            with open(path,'rb') as fileHandler:
                string = fileHandler.read()
                encryptor = Encryptor()
                content = encryptor.DecryptStr(string)
                temp_msg_list = content.split('&*')
                if reverse:
                    temp_msg_list = temp_msg_list[::-1]
                if not offset:
                    msg_list.extend(temp_msg_list)
                elif offset in temp_msg_list:
                    index = temp_msg_list.index(offset)
                    msg_list.extend(temp_msg_list[index+1:])
                    offset = ''
                if len(msg_list)>=segment_size:
                    return msg_list[:segment_size]
        return msg_list[:segment_size]
