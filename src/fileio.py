
from abc import abstractmethod
from collections import defaultdict

from settings import Config
from serializable import SerializableMixin  
from models import Event, Applicant, Decision, Loan 
from writeto import * 

class FileIO():   
    def __init__(self, filename): 
        self.filename = filename 
     
    def save_file(self, d: dict):   
        with open(self.filename, "w") as file: 
            for _,item in d.items():
                file.write(item.to_json() + "\n")  
    def save_row(self, d: SerializableMixin):
        with open(self.filename, "a") as file: 
            file.write(d.to_json() + "\n")  
    def clear_file(self): 
        with open(self.filename, "w") as file: 
            file.write("")  

    @abstractmethod
    def load_file(self) -> dict: ... 
 

class LoanFileIO(FileIO): 
    def __init__(self):
        super().__init__(Config.LOAN_FILE) 
    def load_file(self) -> dict:
        l = {} 
        with open(self.filename, "r") as file: 
            for line in file:
                loan = Loan().from_json(line) 
                l[loan.loan_id] = loan  
        return l 

class ApplicantFileIO(FileIO): 
    def __init__(self):
        super().__init__(Config.APPLICANT_FILE) 
    def load_file(self) -> dict:
        a = {}  
        with open(self.filename, "r") as file: 
            for line in file:
                app = Applicant().from_json(line) 
                a[app.applicant_id] = app  
        return a
    
class DecisionFileIO(FileIO): 
    def __init__(self):
        super().__init__(Config.DECISION_FILE) 
    def load_file(self) -> dict:
        d = {} 
        with open(self.filename, "r") as file: 
            for line in file:
                decision = Decision().from_json(line) 
                d[decision.decision_id] = decision  
        return d  
    
class PolicyFileIO(FileIO): 
    def __init__(self):
        super().__init__(Config.POLICY_FILE) 
    def load_file(self) -> dict:
        d = {} 
        with open(self.filename, "r") as file: 
            for line in file:
                decision = Decision().from_json(line) 
                d[decision.decision_id] = decision  
        return d  

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
    