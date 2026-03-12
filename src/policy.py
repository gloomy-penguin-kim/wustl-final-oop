
from abc import ABC, abstractmethod
from collections import defaultdict
from decimal import Decimal
from typing import Tuple

from events import EventLogger
from managers import DecisionManager
from models import Decision, Loan, Status
from rule import Rule


class Policy(ABC): 
    def __init__(self, events_logger: EventLogger, decision_manager: DecisionManager): 
        Policy.events_logger = events_logger 
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
