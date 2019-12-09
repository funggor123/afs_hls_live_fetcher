import json
import requests
import sys
from enum import Enum

class Response(object):
        def __init__(self, j):
            self.__dict__ = json.loads(j)

class FileType(Enum):
    SEED = 0
    RAW = 1

class Field(Enum):
    ARFS = "arfs"
    AFS = "afs"
    BOTH = ""

class NodeType(Enum):
    RNODE = 0 
    UNODE = 1
    DNODE = 2

class FidType(Enum):
    AFID = 0 

class AFS:
    
    UPLOAD = "/v1/un/upload/file"
    SET_GFID = "/v1/rn/gfid/set"
    CREATE_GFID = "/v1/rn/gfid/create"
    DOWNLOAD = "/v2/dn/file/download"
    
    def __init__(self, params):
        self.rnode_ip = params['rnode_ip']
        self.unode_ip = params['unode_ip']
        self.dnode_ip = params['dnode_ip'] 

        self.unode_port = params['unode_port'] 
        self.rnode_port = params['rnode_port'] 
        self.dnode_port = params['dnode_port'] 

    def get_address(self, node_type):
        protocol = "http://"
        return [
            protocol + self.rnode_ip + ":" + self.rnode_port, 
            protocol + self.unode_ip + ":" + self.unode_port,
            protocol + self.dnode_ip + ":" + self.dnode_port, 
        ][node_type.value]

    def set_gfid(self, gfid, param_value, param_key="afid"):
        data = {'gfid': gfid, 'request_param_key' : param_key, 'request_param_value': param_value}
        try:
            response = requests.request('POST', self.get_address(NodeType.RNODE) + self.SET_GFID, data=data,  allow_redirects=False)
        except requests.exceptions.RequestException as e:
            return None, str(e)
        if self.is_not_success(response):
            return None, "Set Gfid Fail: 404"
        set_gfid_response = Response(response.text)
        return set_gfid_response, self.check(set_gfid_response)

    def create_gfid(self):
        try: 
            response = requests.request('POST', self.get_address(NodeType.RNODE) + self.CREATE_GFID, allow_redirects=False)
        except requests.exceptions.RequestException as e:
            return None, str(e)
        if self.is_not_success(response):
            return None, "Create Gfid Fail: 404"
        create_gfid_response = Response(response.text)
        return create_gfid_response, self.check(create_gfid_response)

    def upload(self, localfilename, expire_days=-1, file_type=FileType.RAW, field=Field.ARFS):
        data = {'expire_days': expire_days, 'upload_type' : file_type.value, 'field': field.value}
        file = {'file': open(localfilename, 'rb')}
        try: 
            response = requests.request('POST', self.get_address(NodeType.UNODE) + self.UPLOAD, data=data, files=file, allow_redirects=False)
        except requests.exceptions.RequestException as e:
            return None, str(e)
        if self.is_not_success(response):
            return None, "Upload Fail: 404"
        upload_response = Response(response.text)
        return upload_response, self.check(upload_response)

    def download(self, localfilename, fid, file_type=FileType.RAW, fid_type=FidType.AFID):
        data = {'file_id': fid, 'fid_type' : file_type.value, 'file_id_format': fid_type.value, 'localfilename' : localfilename}
        try:
            response = requests.get(self.get_address(NodeType.DNODE) + self.DOWNLOAD, data)
        except requests.exceptions.RequestException as e:
            return None, str(e)
        if self.is_not_success(response):
            return None, "Download Fail: 404"
        return response.content, None
        
    def check(self, response):
        if response.status != 1:
            return response.message
        return None
    
    def is_not_success(self, response):
        if response.status_code != 200:
            return True
        return False