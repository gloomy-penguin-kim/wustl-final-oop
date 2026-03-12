
from fileio.fileio import FileIO 
from ..settings import Config
from ..models import Applicant


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