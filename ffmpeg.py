

import signal
import os
from subprocess import PIPE, Popen, STDOUT
import subprocess

class FFmpeg:
    def __init__(self, cmd):
        self.cmd = cmd
        print("_r=info;cmd=" + " ".join(cmd) +";")
        self.proc = None

    def start(self):
        try:
            self.proc = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            return None
        except subprocess.CalledProcessError:
            self.proc = None
        except FileNotFoundError as error:
            self.proc = None
        return "call ffmpeg fail"
    
    def is_started(self):
        return self.proc is not None

    def is_creating_segment_ts(self, line):
        return line.find('Opening') != -1 and line.find('.ts') != -1

    def is_creating_segment_list(self, line):
        return line.find('Opening') != -1 and line.find('.m3u8') != -1

    def is_fail_to_find_video_device(self, line):
        return line.find('Cannot open video device') != -1 

    def is_video_device_busy(self, line):
        return line.find('Device or resource busy') != -1

    def get_file_name_current_segemnt_ts(self, line):
        start_index = line.find("Opening '") + len("Opening '") 
        end_index = line.find(' for') 
        return line[start_index: end_index-1]

    def get_stdout(self):
        if self.is_started():
            return self.proc.stdout
        return None

    def get_stderr(self):
        if self.is_started():
            return self.proc.stderr
        return None

    def kill(self):
        if self.proc != None:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)