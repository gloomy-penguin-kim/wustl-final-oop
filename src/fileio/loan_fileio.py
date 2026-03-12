
from fileio.fileio import FileIO
from models import Loan  
from settings import Config

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