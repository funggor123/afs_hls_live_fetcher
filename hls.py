
import os
import threading
import glob
import requests
import datetime
import json
import subprocess
from enum import Enum
from subprocess import Popen, PIPE, STDOUT
from os         import read
from shutil import copyfile
import os
import threading
import glob
import requests
import datetime
import json
from enum import Enum


class Response(object):
        def __init__(self, j):
            self.__dict__ = json.loads(j)

class UploadType(Enum):
    SEED = 0
    RAW = 1

class AFS:
    def __init__(self, address, unode_port="8074", rnode_port="8072"):
        self.address = address
        self.unode_port = unode_port
        self.rnode_port = rnode_port

    def get_upload_address(self):
        protocol = "http://"
        address = self.address 
        port = ":" + self.unode_port
        postfix = "/v1/un/upload/file"
        return protocol + address + port + postfix

    def get_create_gfid_address(self):
        protocol = "http://"
        address = self.address 
        port = ":" + self.rnode_port
        postfix = "/v1/rn/gfid/create"
        return protocol + address + port + postfix

    def get_set_gfid_address(self):
        protocol = "http://"
        address = self.address 
        port = ":" + self.rnode_port
        postfix = "/v1/rn/gfid/set"
        return protocol + address + port + postfix

    def get_upload_payload(self, expire_days, upload_type):
        return {'expire_days': expire_days, 'upload_type' : upload_type}

    def get_set_gfid_payload(self, gfid, afid):
        return {'gfid': gfid, 'request_param_key' : "afid", 'request_param_value': afid}

    def set_gfid(self, gfid, afid):
        response = requests.request('POST', self.get_set_gfid_address(), data=self.get_set_gfid_payload(gfid, afid),  allow_redirects=False)
        set_gfid_response = Response(response.text)
        return set_gfid_response

    def create_gfid(self):
        response = requests.request('POST', self.get_create_gfid_address(), allow_redirects=False)
        create_gfid_response = Response(response.text)
        return create_gfid_response

    def upload(self, localfilename, expire_days=7, upload_type=UploadType.RAW):
        files = {'file': open(localfilename, 'rb')}
        response = requests.request('POST', self.get_upload_address(), data=self.get_upload_payload(expire_days, upload_type), files=files, allow_redirects=False)
        upload_response = Response(response.text)
        return upload_response

def fetch_from_source():
    afs = AFS("39.108.80.53")
    gfid = afs.create_gfid().gfid
    print(gfid)
    t = datetime.datetime.now()
    prog = 'ffmpeg'
    proc = Popen([prog, '-i', '/dev/video0', '-ss', '00:00:05', '-t', '24:00:00', '-c:v' ,'libx264', '-c:a', 
    'aac', '-f', 'segment', '-segment_time', '2', '-segment_list', str(t)[:10]+ '.m3u8', 'output%04d.ts'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    file_to_upload = None
    afid = None
    for line in proc.stdout:
        line = bytes.decode(line)
        if line.find('Opening') != -1 and line.find('.ts') != -1:
           start_index = line.find("Opening '") + len("Opening '") 
           end_index = line.find(' for') 
           temp = line[start_index: end_index-1]
           if os.path.isfile('./' + str(t)[:10] + '.m3u8' ):
               
                if not os.path.isfile('./' + str(t)[:10] + '_afid.m3u8' ):
                    with open('./' + str(t)[:10]+ '.m3u8', "r") as f:
                        content = f.readlines()
                    with open('./' + str(t)[:10] + '_afid.m3u8', 'w') as f:
                        for i, line in enumerate(content):
                            if i != len(content) - 1:
                                f.write(line)
                        f.write(afid + "\n")
                else: 
                    with open('./' + str(t)[:10]+ '.m3u8', "r") as f:
                        content = f.readlines()
                        content = [x.strip() for x in content] 
                    with open('./' + str(t)[:10] + '_afid.m3u8', 'rb+') as f:
                        f.seek(-1, 2)
                        f.write( ("\n"+ str(content[-2]) + "\n").encode() )
                        f.write( (afid + "\n").encode())
                print("upload :", file_to_upload) 
                if file_to_upload != None:
                        afs.set_gfid(gfid, afs.upload("./"+file_to_upload).afid)    
           file_to_upload = temp
            
        if line.find('Opening') != -1 and line.find('.m3u8') != -1:
            print("upload :", file_to_upload)
            if file_to_upload != None:
                afid = afs.upload("./"+file_to_upload).afid
            file_to_upload = str(t)[:10] + '_afid.m3u8'

        

def start_fetch():
    fetch_from_source()


start_fetch()
