
# from fileio.fileio import FileIO?
# from models import PolicySettings  
# from settings import Config

# class PolicyFileIO(FileIO): 
#     def __init__(self):
#         super().__init__(Config.POLICY_FILE) 
#     def load_file(self) -> dict:
#         d = {} 
#         with open(self.filename, "r") as file: 
#             for line in file:
#                 decision = PolicySettings().from_json(line) 
#                 d[decision.decision_id] = decision  
#         return d  