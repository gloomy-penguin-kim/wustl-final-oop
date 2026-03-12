
from collections import defaultdict

from src.settings import Config
from fileio.fileio import FileIO
from src.writeto import EventWriteToPrint, EventWriteToFile, EventWriteTo
from src.models import Event 

class EventFileIO(FileIO): 
    writeTo = [EventWriteToPrint(), EventWriteToFile()] 
    filename = Config.AUDIT_FILE 
    def __init__(self,  
                 writeTo: list[EventWriteTo] = [EventWriteToPrint(), EventWriteToFile()], 
                 filename:str=Config.AUDIT_FILE):
        super().__init__(filename) 
        EventFileIO.writeTo = writeTo  
        EventFileIO.filename = filename  
    def load_file(self) -> dict:
        e = defaultdict(list)
        with open(self.filename, "r") as file: 
            for line in file:
                event = Event().from_json(line) 
                e[event.loan_id].append(event) 
        return e  
    def write(self, e: Event) -> None: 
        for wt in EventFileIO.writeTo: 
            wt.write(e) 
    def save_file(self, d: dict):   
        with open(self.filename, "w") as file: 
            for _,item in d.items():
                for i in item: 
                    file.write(i.to_json() + "\n") 
    