from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal 
from enum import Enum
from typing import Dict, Tuple, overload, Any
import csv, io, json
from abc import ABC, abstractmethod
import uuid
import os 
from pathlib import Path
 
# class EmailSender(Sender):
#     def send(self, recipient: str, message: str) -> None:
#         print(f"EMAIL → {recipient}: {message}")



class SerializableMixin(ABC):
    """A mixin to add serialization behavior to any class."""
    def to_dict(self) -> dict:
        """Returns a dictionary representation of the object's attributes."""
        # Check if the class uses __slots__, otherwise use __dict__
        d = {}  
        if hasattr(self, "__slots__"):
            d = dict() 
            for name in self.__slots__: 
                d[name] = getattr(self, name)  
                # if isinstance(d[name], uuid.UUID):
                #     d[name] = str(d[name]) 
                if isinstance(d[name], Decimal):
                    d[name] = float(d[name]) 
                if isinstance(d[name], SerializableMixin):
                    d[name] = d[name].to_dict()   
        return d 
    
    def to_json(self) -> str:  
        return json.dumps(self.to_dict(), default=str) 
    
    def to_csv(self):
        buf = io.StringIO()
        to_dict = self.to_dict() 
        writer = csv.DictWriter(buf, fieldnames=to_dict.keys())
        writer.writeheader()
        writer.writerows(to_dict)
        return buf.getvalue()
    
    @abstractmethod
    def from_dict(self, d: dict) -> Any: ... 
     
    def from_json(self, s: str):  
        return self.from_dict(json.loads(s))
    
class EventSerializableMixin(SerializableMixin):
    def from_dict(self, d: dict):
        return Event(event=d["event"], 
                    loan_id=d["loan_id"], 
                    hash_self=d["hash_self"], 
                    hash_prev=d["hash_prev"],
                    timestamp=d["timestamp"])
            
class ApplicantSerialzationMixin(SerializableMixin):
    def from_dict(self, d: dict): 
        return Applicant(applicant_id=d["applicant_id"], 
                         name=d["name"], 
                         annual_income=d["annual_income"], 
                         monthly_debt=d["monthly_debt"],
                         credit_score=d["credit_score"], 
                         employment_status=d["employment_status"], 
                         existing_customer=d["existing_customer"], 
                         created_at=d["created_at"])
      
class LoanSerialzationMixin(SerializableMixin):
    def from_dict(self, d: dict): 
        a = d["applicant"]
        if isinstance(a, str):
            a = Applicant().from_json(a)
        if isinstance(a, dict):
            a = Applicant().from_dict(a)
        if isinstance(a, Applicant): 
            return Loan(loan_id=d["loan_id"], 
                        applicant=a, 
                        requested_amount=d["requested_amount"], 
                        term_months=d["term_months"],
                        purpose=d["purpose"],
                        created_at=d["created_at"])
        else: 
            raise ValueError(f"applicant cannot be parsed: {a}")
     
class DecisionSerialzationMixin(SerializableMixin):
    def from_dict(self, d: dict):
        return Decision(decision_id=d["decision_id"], 
                         status=d["status"], 
                         reason_codes=d["reason_codes"],  
                         approved_amount=d["approved_amount"],  
                         apr=d["apr"], 
                         policy=d["policy"],  
                         created_at=d["created_at"])
     
        
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

class Common(object): 
    ROOT_DIR = "C:\\Homework\\week04\\output"
    AUDIT_FILE = os.path.join(ROOT_DIR, "audit.json") 
    APPLICANT_FILE = os.path.join(ROOT_DIR, "applicant.json") 
    DECISION_FILE = os.path.join(ROOT_DIR, "decision.json") 
    LOAN_FILE = os.path.join(ROOT_DIR, "loan.json") 
    POLICY_FILE = os.path.join(ROOT_DIR, "policy.json") 
Config = Common 

class LoanFileIO(FileIO): 
    def __init__(self):
        super().__init__(Config.LOAN_FILE) 
    def load_file(self) -> dict:
        l = {}
        path = Path(self.filename)
        if path.is_file(): 
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
    
@dataclass(frozen=True, slots=True)
class Event(EventSerializableMixin): 
    event: str | None = None 
    loan_id: uuid.UUID | None = None  
    hash_self: int | None = None 
    hash_prev: int | None = None 
    timestamp: datetime = datetime.now() 

    
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
    
    
class EventWriteTo(ABC): 
    def write(self, event: Event) -> None:...
class EventWriteToFile(EventWriteTo):
    def write(self, event: Event) -> None:
        with open(Config.AUDIT_FILE, "a") as f: 
            f.write(event.to_json() +"\n")
class EventWriteToStringIO(EventWriteTo):
    def write(self, event: Event) -> None:
        buffer = io.StringIO()
        buffer.write(event.to_json() +"\n") 
        buffer.close() 
class EventWriteToPrint(EventWriteTo):
    def write(self, event: Event) -> None:
        print("Emitting Event:", event.loan_id, event.event) 

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

class EventSink(ABC): 
    def __init__(self):  
        pass 

    @abstractmethod 
    def emit(self, event: dict) -> None:...     

class HashChainedAuditMixin(): 
    def audit(self, events: list[Event]):
        prev = None 
        for event in events: 
            if prev and prev != event.hash_prev:
                raise KeyError("Event chain does not match")
            prev = event.hash_self
    
class EventLogger(EventSink, EventFileIO, HashChainedAuditMixin):
    events = defaultdict(list) 
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 
        EventLogger.events = EventLogger.events | self.load_file() 
 
    def emit(self, event: dict) -> None: 
        if "event" not in event: 
            raise KeyError(f"Event is missing valid 'event' string.")  
        e = Event().from_dict(event) 
        EventLogger.events[e.loan_id].append(e) 
        self.audit(EventLogger.events[e.loan_id])
        self.write(e)
    
    def get_hash_prev(self, loan_id: uuid.UUID | None):
        if not loan_id: return 
        if loan_id in EventLogger.events and len(EventLogger.events[loan_id]) > 0: 
            return EventLogger.events[loan_id][-1].hash_self 
    
    def hash(self, d: dict) -> int:
        return hash(d["event"] + str(d["loan_id"]) + str(d["timestamp"])) 
        
    def new(self, event: str, loan_id: uuid.UUID | None, timestamp: datetime = datetime.now()):
        d = {
            "event": event, 
            "loan_id": loan_id, 
            "hash_prev": self.get_hash_prev(loan_id), 
            "timestamp": timestamp 
        }
        d["hash_self"] = self.hash(d) 
        self.emit(d) 
    
    def clean(self, loans: list[uuid.UUID]):
        e = defaultdict(list) 
        for loan_id,event in EventLogger.events.items(): 
            if loan_id in loans: 
                e[loan_id] = EventLogger.events[loan_id][:]
        EventLogger.events = e 
        self.save_file(EventLogger.events)


        



@dataclass(frozen=True, slots=True) 
class Applicant(ApplicantSerialzationMixin): 
    applicant_id: uuid.UUID  | None = None  
    name: str                | None = None  
    annual_income: Decimal   | None = None 
    monthly_debt: Decimal    | None = None 
    credit_score: int        | None = None 
    employment_status: bool  | None = None 
    existing_customer: bool  | None = None 
    created_at: datetime     | None = datetime.now()  

    def __post_init__(self): 
        if self.name and len(self.name.strip()) == 0: 
            raise ValueError("name must be provided") 
        if self.annual_income and self.annual_income < 0:
            raise ValueError("annual income must be 0 or greater") 
        if self.monthly_debt and self.monthly_debt < 0:
            raise ValueError("monthly debt must be 0 or greater") 
        if self.credit_score and (self.credit_score < 300 or self.credit_score > 850): 
            raise ValueError(f"credit score is out of bounds: {self.credit_score}")
                
    def debt_to_income_ratio(self) -> Decimal | None: 
        if self.annual_income and self.monthly_debt:
            monthly_income = self.annual_income / 12  
            return (self.monthly_debt / monthly_income) * 100    
        return None 
 
ALLOWED_LOAN_TERMS = [12,24,26,48,60,72]
@dataclass(frozen=True, slots=True)    
class Loan(LoanSerialzationMixin): 
    loan_id: uuid.UUID          | None = None 
    applicant: Applicant        = Applicant() 
    requested_amount: Decimal   | None = None 
    term_months: int            | None = None 
    purpose: str                | None = None 
    created_at: datetime        | None = datetime.now()   
    def __post_init__(self):  
        if self.requested_amount and self.requested_amount <= 0:
            raise ValueError("requested amount must be greater than 0") 
        if self.term_months and self.term_months not in ALLOWED_LOAN_TERMS:
            raise ValueError(f"term month not in allowed terms: {self.term_months}, must be in: {ALLOWED_LOAN_TERMS}") 
        if self.purpose and len(self.purpose.strip()) == 0: 
            raise ValueError("purpose must be provided") 
        
    def calculate_simple_interest(self, principal, annual_rate, years):
        # Convert annual percentage rate to a decimal
        rate_decimal = annual_rate / 100 
        interest = principal * rate_decimal * years
         
        return interest
     
class Status(Enum): 
    APPROVE = 1
    DECLINE = 2 
    REFER   = 3  
    INVALID = 4

@dataclass(frozen=True, slots=True)
class Decision(DecisionSerialzationMixin): 
    decision_id: uuid.UUID   | None = None 
    loan_id: uuid.UUID      | None = None 
    status: Status          | None = None 
    reason_codes: list[str] | None = None 
    approved_amount: Decimal | None = None 
    apr: Decimal            | None = None   
    policy: str             | None = None 
    created_at: datetime    | None = datetime.now()  
    def copy(self):
        return Decision(self.decision_id,
                        self.loan_id,
                        self.status,
                        self.reason_codes,
                        self.approved_amount, 
                        self.apr,
                        self.policy,
                        self.created_at)  

    def __str__(self): 
        return f"Decision[{self.decision_id}, {self.status}, {self.reason_codes}, {self.approved_amount}, {self.apr}]"
 
    def __post_init__(self):    
        if self.reason_codes:
            if len(self.reason_codes) <= 0:
                raise ValueError("reason code list length must be greater than 0")   
            list_reason_codes = sorted(list(set(self.reason_codes))) 
            if len(self.reason_codes) != len(set(self.reason_codes)):
                raise ValueError(f"reason code list is not unique: {self.reason_codes}")  
            if self.reason_codes != list_reason_codes:
                raise ValueError(f"reason code list is not sorted: {self.reason_codes}, {list_reason_codes}") 
            
        if self.approved_amount and self.approved_amount < 0:
            raise ValueError("approved amount must be greater than 0")
        
        if self.status == Status.DECLINE:
            if self.approved_amount:
                raise ValueError("approved amount must be None for DECLINED")
            if self.apr:
                raise ValueError("apr amount must must be None for DECLINED")
            
        if self.status == Status.APPROVE:
            if self.approved_amount and self.approved_amount <= 0:
                raise ValueError("approved amount must be greater than 0 for APPROVED")
            if self.apr and self.apr <= 0:
                raise ValueError("apr amount must be greater than 0 for APPROVED")


    
class LoanManager(LoanFileIO): 
    loans: Dict[uuid.UUID, Loan] = {}   
    def __init__(self, events: EventLogger, **kwargs):  
        super().__init__(**kwargs)  
        self.load() 
        self.events_logger = events
        pass
    def new(self, applicant: Applicant, requested_amount: Decimal, term_months: int, purpose: str): 
        loan_id = uuid.uuid4() 
        loan = Loan(loan_id, 
                    applicant=applicant, 
                    requested_amount=requested_amount, 
                    term_months=term_months, 
                    purpose=purpose, 
                    created_at=datetime.now())
        LoanManager.loans[loan_id] = loan 
        self.save_row(loan) 
        self.events_logger.new(event="submitted", loan_id=loan_id)
        return loan 
    def load(self): 
        LoanManager.loans = self.load_file() 
        print("loaded applicants:", len(LoanManager.loans))
    @overload
    def get(self, loan_id: str) -> Loan | None: 
        loan_idd = uuid.UUID(loan_id)
        return self.get(loan_idd)    
    @overload
    def get(self, loan_id: uuid.UUID) -> Loan | None:  
        if loan_id in LoanManager.loans: 
            return LoanManager.loans[loan_id]    

 
    
class ApplicantManager(ApplicantFileIO): 
    applicants = {}   
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)
        self.load()  
    def new(self, name: str, annual_income: Decimal, monthly_debt: Decimal, 
                      credit_score: int, employment_status: bool, existing_customer: bool):
        app_id = uuid.uuid4() 
        applicant = Applicant(app_id, 
                              name=name, 
                              annual_income=annual_income, 
                              monthly_debt=monthly_debt, 
                              credit_score=credit_score, 
                              employment_status=employment_status, 
                              existing_customer=existing_customer, 
                              created_at=datetime.now())
        ApplicantManager.applicants[app_id] = applicant 
        self.save_row(applicant)
        return applicant 
    def load(self): 
        ApplicantManager.applicants = self.load_file() 
        print("loaded applicants:", len(ApplicantManager.applicants))
    @overload
    def get(self, app_id: str) -> Loan | None: 
        app_idd = uuid.UUID(app_id)
        return self.get(app_idd)    
    @overload
    def get(self, app_id: uuid.UUID) -> Loan | None:  
        if app_id in ApplicantManager.applicants: 
            return ApplicantManager.applicants[app_id]      

class DecisionManager(DecisionFileIO):         
    decisions = {}  
    def __init__(self, events: EventLogger, **kwargs):
        super().__init__(**kwargs) 
        self.events_logger = events  
        self.load() 
    def new(self, loan_id: uuid.UUID | None, status: Status | None, reason_codes: list[str] | None, 
            approved_amount: Decimal | None, apr: Decimal | None, policy: str):
        decision_id = uuid.uuid4() 
        decision = Decision(decision_id,
                            loan_id,  
                            status=status, 
                            reason_codes=reason_codes, 
                            approved_amount=approved_amount,
                            apr=apr, 
                            policy=policy, 
                            created_at=datetime.now())
        DecisionManager.decisions[decision_id] = decision 
        self.save_row(decision)
        self.events_logger.new("decisioned", loan_id)
        return decision 
    def save(self, d: Decision):  
        decision = d.copy()
        DecisionManager.decisions[d.decision_id] = decision  
        self.save_row(decision) 
    def load(self): 
        DecisionManager.decisions = self.load_file() 
    @overload
    def get(self, decision_id: str) -> Decision | None: 
        decision_idd = uuid.UUID(decision_id)
        return self.get(decision_idd)    
    @overload
    def get(self, app_id: uuid.UUID) -> Decision | None:  
        if app_id in DecisionManager.decisions: 
            return DecisionManager.decisions[app_id]  

LOW = Decimal(0.09)
MEDIUM = Decimal(0.16)
HIGH = Decimal(0.22)

@dataclass 
class RuleResult: 
    status: Status  | None = None 
    code: str       | None = None 
    apr:  Decimal   | None = None 
class Rule(ABC): 
    @abstractmethod
    def apply(self, loan: Loan, ctx: dict) -> RuleResult:...  

class Rule_DTI_Lte_30(Rule): 
    def __init__(self): 
        self.code = "DIT30" 
        self.reason = "DTI is below 30"
    def apply(self, loan: Loan, ctx: dict) -> RuleResult: 
        dti = loan.applicant.debt_to_income_ratio() 
        if (dti and dti <= 30): 
            ctx[Status.APPROVE].append(self.code)
            return RuleResult(apr=LOW, status=Status.APPROVE, code=self.code)
        return RuleResult()  
 
# class Rule_Credit_Score_Gte_775(Rule): 
#     def __init__(self): 
#         self.code = "CS775" 
#         self.reason = "credit score is above 800"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if loan.applicant.credit_score and loan.applicant.credit_score >= 800: 
#             ctx[Status.APPROVE].append(code=self.code)
#             return RuleResult(apr=LOW, status=Status.APPROVE, code=self.code)
#         return RuleResult()  

# class Rule_DTI_Gte_50(Rule): 
#     def __init__(self): 
#         self.code = "DT050" 
#         self.reason = "DTI is high"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if (loan.applicant.debt_to_income_ratio() >= 50): 
#             ctx[Status.DECLINE].append(self.code)
#             return RuleResult(status=Status.DECLINE, code=self.code) 
#         elif (loan.applicant.debt_to_income_ratio() > 47): 
#             ctx[Status.REFER].append(self.code)
#             return RuleResult(apr=HIGH, status=Status.REFER, code=self.code)
#         return RuleResult()  
 
# class Rule_Annual_Income(Rule): 
#     def __init__(self): 
#         self.code = "AI200" 
#         self.reason = "annual income must exceed requested amount" 
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if loan.applicant.annual_income and loan.requested_amount and loan.term_months and loan.applicant.monthly_debt: 
#             if (loan.applicant.annual_income >= (loan.requested_amount/loan.term_months)*12*3): 
#                 ctx[Status.APPROVE].append(self.code)
#                 return RuleResult(apr=LOW, status=Status.APPROVE, code=self.code)
#             elif (loan.applicant.annual_income-Decimal(loan.applicant.monthly_debt*12) >= (loan.requested_amount/loan.term_months)*12): 
#                 ctx[Status.REFER].append(self.code)
#                 return RuleResult(apr=MEDIUM, status=Status.REFER, code=self.code)
#             else: 
#                 ctx[Status.DECLINE].append(self.code)
#                 return RuleResult(status=Status.DECLINE, code=self.code)  
#         return RuleResult() 

# class Rule_DTI_Lte_43_and_Credit_Score_Gte_715_and_Employeed(Rule): 
#     def __init__(self): 
#         self.code = "DT143" 
#         self.reason = "DTI <= 43, credit score >= 715 and employed"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if ((loan.applicant.debt_to_income_ratio() <= 43) and 
#             (loan.applicant.credit_score and loan.applicant.credit_score >= 715)):
#             if (loan.applicant.employment_status and loan.applicant.employment_status): 
#                 ctx[Status.APPROVE].append(self.code)
#                 return RuleResult(apr=MEDIUM, status=Status.APPROVE, code=self.code)
#         return RuleResult()   

# class Rule_Previous_Customer(Rule): 
#     def __init__(self): 
#         self.code = "EC100" 
#         self.reason = "DTI <= 43, credit score >= 625 and existing customer"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if ((loan.applicant.debt_to_income_ratio() <= 43) and 
#            (loan.applicant.credit_score and loan.applicant.credit_score >= 625)):  
#             if (loan.applicant.existing_customer): 
#                 ctx[Status.APPROVE].append(self.code)
#                 return RuleResult(apr=MEDIUM, status=Status.APPROVE, code=self.code)
#         return RuleResult()  

# class Rule_Refer(Rule): 
#     def __init__(self): 
#         self.code = "ZC100" 
#         self.reason = "DTI <= 50, credit score >= 700 and existing customer or employed"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if ((loan.applicant.debt_to_income_ratio() <= 50) and 
#            (loan.applicant.credit_score and loan.applicant.credit_score >= 700) and 
#            (loan.applicant.existing_customer or loan.applicant.employment_status)):  
#             ctx[Status.APPROVE].append(self.code)
#             return RuleResult(apr=MEDIUM, status=Status.APPROVE, code=self.code)
#         return RuleResult()  
 


class Policy(ABC): 
    def __init__(self, events_logger: EventLogger, decision_manager: DecisionManager): 
        Policy.events_logger = events 
        Policy.decision_manager = decision_manager  
            
    @abstractmethod
    def evaluate(self, loan: Loan) -> Tuple[Decision, dict]:... 
    def calculate_stated_apr(self, principal, total_interest, total_fees, loan_term_days): 
        total_cost = total_interest + total_fees
        rate_per_day = (total_cost / principal) / Decimal(loan_term_days)
        annual_rate = rate_per_day * Decimal(365)
        apr = annual_rate * Decimal(100)
        return round(apr, 2)
    
class RuleBasedPolicy(Policy):
    def __init__(self, rules: list[Rule], name: str, **kwargs):
        super().__init__(**kwargs) 
        self.rules = rules 
        self.name = name 

    def evaluate(self, loan: Loan) -> Tuple[Decision, dict]: 
        Policy.events_logger.new(event="policy_selected", loan_id=loan.loan_id)
        ctx = defaultdict(list)
        rr = defaultdict(list)
        for r in self.rules: 
            result = r.apply(loan, ctx) 
            rr[result.status].append(result)  

        Policy.events_logger.new(event="policy_evaluated", loan_id=loan.loan_id)

        if len(rr[Status.DECLINE]) > 0:
            codes = sorted([r.code for r in rr[Status.DECLINE]])
            d = self.decision_manager.new(loan_id=loan.loan_id, 
                                    status=Status.DECLINE,  
                                    reason_codes=codes, 
                                    approved_amount=None, 
                                    apr=None, 
                                    policy=self.name)
            return (d, ctx) 
            

        elif len(rr[Status.REFER]) > 0 or len(rr[Status.APPROVE]) == 0:
            codes = sorted([r.code for r in rr[Status.REFER]])
            if len(codes) == 0: 
                codes.append("default") 
            d = self.decision_manager.new(loan_id=loan.loan_id, 
                                    status=Status.REFER,  
                                    reason_codes=codes, 
                                    approved_amount=Decimal(0), 
                                    apr=Decimal(0), 
                                    policy=self.name)
            return (d, ctx) 

        else: 
            codes = sorted([r.code for r in rr[Status.APPROVE]])
            apr = 0
            if loan.requested_amount and loan.term_months: 
                apr = self.calculate_stated_apr(loan.requested_amount, loan.requested_amount*Decimal(.25), 0, loan.term_months*30)
            else: 
                r = [r.apr for r in rr[Status.APPROVE]] 
                apr = sum(r) / len(r) 
            d = self.decision_manager.new(loan_id=loan.loan_id, 
                                    status=Status.APPROVE,  
                                    reason_codes=codes, 
                                    approved_amount=loan.requested_amount, 
                                    apr=Decimal(apr), 
                                    policy=self.name)
            return (d, ctx) 
 
    
class ScoreBoardPolicy(Policy): 
    def evaluate(self, loan: Loan) -> Tuple[Decision, dict]:  
        return (Decision(), dict())

class HybridPolicy(Policy): 
    def evaluate(self, loan: Loan) -> Tuple[Decision, dict]:  
        return (Decision(), dict())

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

 