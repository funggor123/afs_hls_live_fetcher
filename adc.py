
import requests
import time
import subprocess
import platform
from afs import Response
from enum import Enum

class AdcEndpoint(Enum):
    GET_CONTRACT = '/contract/q/'

class Adc:
    USER_ADDR = "1PvC5qEsiztmNG6fp31sMGEWrVeC7nfsaM"
    USER_PUB = "9c6dfc6cec22a9ae105b5674dc0a4edc443f5860ed27142e5422e91b29432d761b11370588f6af737fce138d3139c00486f464fe5ae1800544c7d31f56cd5ae4"
    USER_PRIV = "2d2d2d2d2d424547494e2050524956415445204b45592d2d2d2d2d0a4d4863434151454549452b424a6d3231673065533875344b45346e31464e73705a432b61703463393171776f4f7452744e6263796f416f4743437147534d34390a417745486f555144516741456e473338624f77697161345157315a303341704f3345512f574744744a78517556434c7047796c444c58596245546346695061760a63332f4f453430784f6341456876526b2f6c72686741564578394d665673316135413d3d0a2d2d2d2d2d454e442050524956415445204b45592d2d2d2d2d0a"

    def __init__(self, params, afs):
        self.adc_ip = params['adc_ip']
        self.adc_port = params['adc_port']
        self.afs = afs

    def get_address(self):
        protocol = "http://"
        return protocol + self.adc_ip + ":" + self.adc_port

    def get_contract(self, contract_id):
        response = requests.get(self.get_address() + AdcEndpoint.GET_CONTRACT + contract_id)
        get_contract_response = Response(response.text)
        return get_contract_response

    def submit_task(self, script_file_path):
        upload_response = afs.upload(script_file_path)
        unsigned_ticket = create_new_task_request(upload_response.afid) 
        signature = sign_data(unsigned_ticket["data2Sign"])
        unsigned_ticket["signature"] = signature 
        unsigned_ticket["pubkey"] = USER_PUB
        contract_id = confirm_with_signature(unsigned_ticket) #conform the signed contract and start job
        return contract_id

    def create_new_task_request(self, script_afid):
        r = requests.post("{}/contract/computation".format(self.get_address()),
            json={
                "address": USER_ADDR,
                "script": script_afid,
                "name": "task" + "{}".format(int(time.time())),
                "bounty": 1,
                "taskTime": 3600,
                "numRequired": 1,
                "os":"linux",
                "arch":"amd64"
            })
        if r.status_code == 200 and r.json()["code"] == 0 and r.json()["data"]["serializedCt"] != None and r.json()["data"] != None and r.json()["data"]["ctID"] != None and r.json()["data"]["data2Sign"] != None and r.json()["data"]["data2Sign"] != "":
            unsigned_ticket = r.json()["data"]
            print("OK:submitted new task request\n{}".format(r.json()["data"]["ctID"]))
        else:
            print("FAILED:\n{}".format(r.text))
            exit(1)
        return unsigned_ticket

    def sign_data(self, data):
        sign_cmd = "./sign_linux {} {}".format(USER_PRIV, data)
        if platform.system() == "Windows":
            sign_cmd = ".\\sign_win.exe {} {}".format(USER_PRIV, data)
        proc = subprocess.Popen(sign_cmd, stdout=subprocess.PIPE, shell=True)
        signature = proc.stdout.read().decode("utf-8").rstrip("\n\r")
        if signature == None or signature == "":
            print("FAILED:\n")
            exit(1)
            return
        print("OK:signature:\n{}".format(signature))
        return signature

    def confirm_with_signature(self, signed_ticket):
        if signed_ticket["data2Sign"] == None or signed_ticket["data2Sign"] == "":
            print("FAILED:\ninvalid signed payload")
            exit(1)
            return
        r = requests.post("{}/contract/computation/confirmation".format(self.get_address()),
            json={
                "signedSt": signed_ticket
            })
        if r.status_code == 200 and r.json()["data"] != None and r.json()["data"]["stID"] != None and r.json()["data"]["stID"] != "" and r.json()["data"]["ctID"] != None and r.json()["data"]["ctID"] != "":
            return_con_contract = "{}".format(r.json()["data"]["ctID"])
            print("OK:\n{}".format(r.json()["data"]["ctID"]))
        else:
            print("FAILED:\n{}".format(r.text))
            exit(1)
        return return_con_contract
