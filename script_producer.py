import time

class TaskType(Enum):
        DS_SEPERATION = 0
        
class ScriptProducer:
    def make_ds_seperation_task_script(self, m3u8_TS_AFID):

        detect_AFID = "1e00000000001f7f4719b144b6af1610373ecf14a56b0cb5003912d75011c3d29437fa836b646ba988e00fdffc360c448169c952de462dd488f30b4d4d3a41ad"
        d_img_ID = "c7b5122f59ce"			
        d_img_AFID = '1e000000000032cbdcd704a3768e94f760bd4d7efe1a8146efb93369804cdc6c8be680188b62028d3cf989faed061fc943cdea2e5efee007aa52ab68a80cb95b'

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
        return f.name