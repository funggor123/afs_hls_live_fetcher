class Live:
    def __init__(self, agfid):
        
        self.agfid = agfid
        self.afid_m3u8 = None
        self.m3u8 = None
        self.cts_abs_path = None
        self.cts_afid = None
        self.num_of_ts = 0
    
    def get_agfid(self):
        return self.agfid

    def set_m3u8(self, m3u8):
        self.m3u8 = m3u8

    def set_afid_m3u8(self, afid_m3u8):
        self.afid_m3u8 = afid_m3u8

    def get_afid_m3u8(self):
        return self.afid_m3u8