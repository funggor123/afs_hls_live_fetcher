# -*- coding: utf-8 -*-
import json, os, platform, random, requests, subprocess, sys, time
import threading
import glob
import datetime
#addr of the adc and afs node
ADC_ROOT = "http://10.6.71.125:8002"
AFS_RN_ROOT = "http://10.6.71.51:8074/v1/un/upload/"
#afid of all the data and script

USER_ADDR = "1PvC5qEsiztmNG6fp31sMGEWrVeC7nfsaM"
USER_PUB = "9c6dfc6cec22a9ae105b5674dc0a4edc443f5860ed27142e5422e91b29432d761b11370588f6af737fce138d3139c00486f464fe5ae1800544c7d31f56cd5ae4"
USER_PRIV = "2d2d2d2d2d424547494e2050524956415445204b45592d2d2d2d2d0a4d4863434151454549452b424a6d3231673065533875344b45346e31464e73705a432b61703463393171776f4f7452744e6263796f416f4743437147534d34390a417745486f555144516741456e473338624f77697161345157315a303341704f3345512f574744744a78517556434c7047796c444c58596245546346695061760a63332f4f453430784f6341456876526b2f6c72686741564578394d665673316135413d3d0a2d2d2d2d2d454e442050524956415445204b45592d2d2d2d2d0a"

m3u8_TS_AFID = ""
detect_AFID = "1e00000000001f7f4719b144b6af1610373ecf14a56b0cb5003912d75011c3d29437fa836b646ba988e00fdffc360c448169c952de462dd488f30b4d4d3a41ad"

def task_submit(m3u8_TS_AFID):
    script_filepath = create_task_script(m3u8_TS_AFID)
    script_afid = upload_to_afs(script_filepath)
    unsigned_ticket = create_new_task_request(script_afid) #getting unsigned ticket after posting new contract
    signature = sign_data(unsigned_ticket["data2Sign"]) #sign it using the ./sign_linux or if you are using other system ./sign_(OS)
    unsigned_ticket["signature"] = signature 
    unsigned_ticket["pubkey"] = USER_PUB
    contract_id = confirm_with_signature(unsigned_ticket) #conform the signed contract and start job
    return contract_id
#docker image ID
d_img_ID = "c7b5122f59ce"			
d_img_AFID = '1e000000000032cbdcd704a3768e94f760bd4d7efe1a8146efb93369804cdc6c8be680188b62028d3cf989faed061fc943cdea2e5efee007aa52ab68a80cb95b'
#making task script
def create_task_script(m3u8_TS_AFID):
    try:
        with open("mc_script_{}.txt".format(int(time.time())), "w+") as f:
            dkcn = "docker-{}".format(time.time())
            f.write(																	#syntax: ;_(command)
                ";_dk={};_afid={};_dk_name={}\n".format(d_img_ID,d_img_AFID,dkcn) +  #first line : dk = dockerID, afid = docker AFID, dk_name docker container name (should be noted that this should be unique)
                ";_f=wget;_afidR="+ m3u8_TS_AFID + ";_file=video.ts;\n" + #f=wget = download, afid = data's AFID, file = data's name after download
                ";_f=wget;_afidS="+ detect_AFID + ";_file=detect;\n" + 
                ";_f=system;command=docker run -d -P -it --name {} -v \"$PWD/share-data\":/data {};\n".format(dkcn,d_img_ID) + # f=systen = running bash command (not recommanded, for dev purpose)
                ";_f=system;command=docker exec   {} bash -c \"cd /data  && mkdir output_json && chmod +x ./detect &&./detect\";\n".format(dkcn)
                # ";_f=system;command=docker exec   {} bash -c \"cd /data && mv report.m3u8 output_json/\";\n".format(dkcn)
                #";_f=system;command=docker rm -f adc-ffmpeg;\n"
                )
        f.close()
    except Exception as e:
        print("FAILED:\n{}".format(e))
        exit(1)
    print("OK:created task script")
    print(f.name)
    return f.name
#upload the data or the script to the AFS 
def upload_to_afs(filepath):
    afid = ""
    try:
        r = requests.post("{}/file?field=afs".format(AFS_RN_ROOT), files={
                "file": open(filepath, "rb"),
            }, data={
                "upload_type" : 1,
                "expire_days": 10

            })
    except Exception as e:
        print("FAILED\n:{}".format(e))
        exit(1)
    finally:
        os.remove(filepath)
    
    if r.status_code == 200 and r.json()["status"] > -1 :
        afid = r.json()["afid"]
        #print("OK:\n{}".format(r.text))
    else:
        print("FAILED:\n{}".format(r.json()["message"]))
        exit(1)
    print("OK:uploaded to afs:\n{}".format(afid))
    return afid

#follow this json format for task submittion, 
def create_new_task_request(script_afid):
    r = requests.post("{}/contract/computation".format(ADC_ROOT),
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

def sign_data(data):
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

def confirm_with_signature(signed_ticket):
    if signed_ticket["data2Sign"] == None or signed_ticket["data2Sign"] == "":
        print("FAILED:\ninvalid signed payload")
        exit(1)
        return
    r = requests.post("{}/contract/computation/confirmation".format(ADC_ROOT),
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



if __name__ == '__main__':
    pass
