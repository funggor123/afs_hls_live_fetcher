import datetime
from ffmpeg import FFmpeg
from live import Live
from m3u8 import M3U8
import os
from afs import AFS
from timeit import default_timer as timer
from adc import Adc
import logging

class Fetcher:
    def __init__(self, params):
       self.afs = AFS(params)
       self.adc = Adc(params, afs=self.afs)
       
    def get_live_command(self, params):
        prog = 'ffmpeg'
        return [prog, '-i', params['device_mount_point'] , '-c:v' ,'libx264', '-c:a', 
        'aac', '-f', 'segment', '-segment_time', str(params['segement_time']), '-hls_list_size', '5', '-segment_list', params['segment_list_file_abs_path'], '%04d.ts']

    def is_m3u8_file_exists(self, params):
        return os.path.isfile(params['segment_list_file_abs_path'])

    def is_afid_m3u8_file_exists(self, params):
        return os.path.isfile(params['segment_afid_list_file_abs_path'])
        
    def start(self, agfid, device_name, temp_file_dir):   
        
        params = {
            'segment_list_file_abs_path' : temp_file_dir + str(datetime.datetime.now())[:10] + '.m3u8',
            'segment_afid_list_file_abs_path' : temp_file_dir + str(datetime.datetime.now())[:10] + '_afid.m3u8',
            'segement_time' : 8,
            'device_mount_point': '/dev/' + device_name
        } 
        self.ffmpeg = FFmpeg(self.get_live_command(params))
        
        live = None
        if agfid == "":
            res, err = self.afs.create_gfid()
            if err is not None:
                return err
        live = Live(res.agfid) 
        
        err = self.ffmpeg.start()
        start = timer()
        now = datetime.datetime.now()
        live_time = now
        
        for line in self.ffmpeg.get_stdout():
                line = line.decode()
                if self.ffmpeg.is_fail_to_find_video_device(line):
                    err = "cannot find video device " + params['device_mount_point']
                    return err

                if self.ffmpeg.is_video_device_busy(line):
                    err =  "cannot connect to video device " + params['device_mount_point'] + " since it is busy"
                    return err

                if self.ffmpeg.is_creating_segment_ts(line):
                    if is_m3u8_file_exists(params):
                        m3u8 = M3U8(params['segment_list_file_abs_path'])
                        afid_m3u8 = None
                        if not is_afid_m3u8_file_exists(params):
                            contents = m3u8.get_contents(m3u8.get_number_of_line()-1)
                            afid_m3u8 = M3U8(params['segment_afid_list_file_abs_path'])
                            afid_m3u8.create_from_contents(contents)
                            afid_m3u8.append_end("\n")
                            afid_m3u8.append_end(live.cts_afid)
                        else:
                            contents = m3u8.get_contents(m3u8.get_number_of_line()-1)
                            afid_m3u8 = M3U8(params['segment_afid_list_file_abs_path'])
                            afid_m3u8.append_end("\n")
                            afid_m3u8.append_end(contents[-1])
                            afid_m3u8.append_end(live.cts_afid)
                        live.set_afid_m3u8(afid_m3u8)
                        live.set_m3u8(m3u8)
                
                        res, err = self.afs.upload(live.get_afid_m3u8().abs_path)
                        if err is not None:
                            return err
                        res, err = self.afs.set_gfid(live.get_agfid(), res.afid) 
                        if err is not None:
                            return err
                        
                    live.num_of_ts = live.num_of_ts + 1
                    live_time += datetime.timedelta(0,params['segement_time'])

                cmd_out = "live_start=" + now.strftime("%Y-%m-%d %H:%M:%S") + ";lastest_up_cdn=" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ";num_of_ts="+ str(live.num_of_ts) +";live_time="+ live_time.strftime("%Y-%m-%d %H:%M:%S") + ";agfid=" + live.agfid + ";"
                print(cmd_out, flush=True)
                logging.info(cmd_out)
                live.cts_abs_path = self.ffmpeg.get_file_name_current_segemnt_ts(line)  

                if self.ffmpeg.is_creating_segment_list(line):
                    if live.cts_abs_path != None:
                        res = self.afs.upload(live.cts_abs_path)
                        if err is not None:
                            return err
                        live.cts_afid = res.afid
                        os.remove(live.cts_abs_path)
        return err


