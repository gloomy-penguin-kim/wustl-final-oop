import os
 
class Settings(object): 
    ROOT_DIR = "C:\\Homework\\week04\\output"

    AUDIT_FILE = os.path.join(ROOT_DIR, "audit.json") 
    APPLICANT_FILE = os.path.join(ROOT_DIR, "applicant.json") 
    DECISION_FILE = os.path.join(ROOT_DIR, "decision.json") 
    LOAN_FILE = os.path.join(ROOT_DIR, "loan.json") 
    POLICY_FILE = os.path.join(ROOT_DIR, "policy.json") 

Config = Settings 