
from fileio.fileio import FileIO
from ..models import Decision 
from ..settings import Config

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