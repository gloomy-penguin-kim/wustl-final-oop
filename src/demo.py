from __future__ import annotations 
from dataclasses import dataclass 
from decimal import Decimal  
  
from events import EventLogger
from policy import RuleBasedPolicy
from managers import ApplicantManager, DecisionManager, LoanManager
from rule import *
 
# class EmailSender(Sender):
#     def send(self, recipient: str, message: str) -> None:
#         print(f"EMAIL → {recipient}: {message}")


         

# @dataclass(frozen=True, slots=True)
# class Event(SerializableMixin): 
#     event: str | None = None 
#     loan_id: uuid.UUID | None = None  
#     hash_self: int | None = None 
#     hash_prev: int | None = None 
#     timestamp: datetime = datetime.now() 

#     def from_dict(self, d: dict):
#         return Event(event=d["event"], 
#                     loan_id=d["loan_id"], 
#                     hash_self=d["hash_self"], 
#                     hash_prev=d["hash_prev"],
#                     timestamp=d["timestamp"])
     
    
# class PolicyType(Enum): 
#     RULE = 1
#     SCORE = 2 
#     HYBRID = 3       

# @dataclass(frozen=True, slots=True)
# class PolicyData(EventSerializableMixin): 
#     name: str | None = None 
#     type: PolicyType | None = None  
#     rules: list[Rule] | None = None 
#     hash_prev: int | None = None 
#     timestamp: datetime = datetime.now() 
    
    

        




# class PolicyManager(PolicyFileIO):         
#     policies = {}  
#     def __init__(self, event_logger: EventLogger, decision_manager: DecisionManager, **kwargs):
#         super().__init__(**kwargs) 
#         self.events_logger = event_logger  
#         self.decision_manager = decision_manager  
#         self.load() 
#     def new(self, name: str, type: PolicyType, rules: list[Rule] | None):
#         p = None  
#         if type == PolicyType.RULE: 
#             if not rules: rules = [] 
#             p = RuleBasedPolicy(rules, name)   
#         elif type == PolicyType.SCORE:
#             p = ScoreBoardPolicy(name, self.events_logger, self.decision_manager)
#         PolicyManager.policies[name] = p 
#         self.save_row(p)
#         self.events_logger.new("decisioned", loan_id)
#         return decision 
#     def save(self, d: Decision):  
#         decision = d.copy()
#         DecisionManager.decisions[d.decision_id] = decision  
#         self.save_row(decision) 
#     def load(self): 
#         DecisionManager.decisions = self.load_file() 
#     @overload
#     def get(self, decision_id: str) -> Decision | None: 
#         decision_idd = uuid.UUID(decision_id)
#         return self.get(decision_idd)    
#     @overload
#     def get(self, app_id: uuid.UUID) -> Decision | None:  
#         if app_id in DecisionManager.decisions: 
#             return DecisionManager.decisions[app_id]  
 

events = EventLogger() 

apps = ApplicantManager()
loans = LoanManager(events) 

events.clean(loans.loans.keys())

decisions = DecisionManager(events) 

# rules = [Rule_Refer(), Rule_Previous_Customer(), Rule_DTI_Lte_43_and_Credit_Score_Gte_715_and_Employeed(), Rule_Annual_Income(),
# Rule_DTI_Gte_50(), Rule_Credit_Score_Gte_775(), 
rules = [Rule_DTI_Lte_30()]
 
 

ruleDecisions = RuleBasedPolicy(rules=rules, name="RuleBased", events_logger=events, decision_manager=decisions)
 
a = apps.new("kim", Decimal(20), Decimal(2), 755, True, True)
l = loans.new(a, Decimal(20), 12, "puppy dog loan")

a2 = apps.new("peter", Decimal(300), Decimal(55), 820, True, False)
l2 = loans.new(a, Decimal(150), 24, "idk lol money")

d = ruleDecisions.evaluate(l) 

application_id = "123"
name = "RuleBased2.0"

for loan_id in events.events: 
    print(loan_id, "---------------------------")
    for e in events.events[loan_id]: 
        print(e.loan_id, e.event) 

 



# a = Applicant("123", "kim", Decimal(20), Decimal(2), 755, True, True)
# l = Loan("111", a, Decimal(10), 12, "taco bell")
# print(l.to_json())
# d = l.to_dict()
# print(d) 
# d["applicant"] = '{"applicant_id": "123", "name": "kim", "annual_income": 20.0, "monthly_debt": 2.0, "credit_score": 755, "employment_status": true, "existing_customer": true, "created_at": "2026-03-11 00:16:39.308182"}'
# l = Loan().from_dict(d) 
# print(l) 
# print(l.to_json())

 