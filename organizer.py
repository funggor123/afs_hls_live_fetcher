from tinydb import TinyDB, Query
from enum import Enum
import requests
import threading
import time

class Organizer:
    monitor_task_per_second = 3.0
    def __init__(self, adc):
       self.filename = time.strftime("%Y%m%d-%H%M%S") + '.json'
       self.adc = adc
       self.contract_monitor = threading.Timer(monitor_task_per_second, self.monitor) 

    def start_contract_monitor(self):
       self.contract_monitor.start()
    
    def monitor(self):
        db = TinyDB(self.filename)
        contracts = db.all()
        for contract in contracts:
            if contract.data.isClosed is True:
                for worker_result in contract.data.Worker_results:
                    if worker_result.report != "":
                        print(worker_result.report) 
                        ## TODO
                        ## Produce the M3u8
                self.delete_contract(contract['id'])

    def delete_contract(self, db, contract_id):
        Contract = Query()
        db.remove(Contract.id == contract_id)
    
    def add_contract(self, contract_id, ts_fid):
        db = TinyDB(self.filename)
        db.insert({'contract_id': contract_id, 'ts_fid' : ts_fid})









