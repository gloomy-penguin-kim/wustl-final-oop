
from abc import abstractmethod 
 
from serializable import SerializableMixin  


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