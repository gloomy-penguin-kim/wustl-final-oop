from __future__ import annotations
from decimal import Decimal
from typing import Any, overload
 

from app.persistence.json_store import JsonStore
from app.domain.application import LoanApplication
from app.audit.event_sink import FileEventSink, PrintEventSink
from app.domain.application import Applicant
from app.wrappers.wrapper import Wrapper
 
 
class Loans(Wrapper, JsonStore, PrintEventSink, FileEventSink):  
    items = {} 
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        Loans.items = Loans.items | self.load_by_type()

    def register(self, item: LoanApplication) -> None:
        self._add_item(item)  
 
    @overload
    def new(self, d: dict) -> LoanApplication:...
    
    @overload
    def new(self, 
            applicant: Applicant, 
            requested_amount: Decimal, 
            term_months: int, 
            purpose: str,
            application_id: str | None = None) -> LoanApplication:...
 
    def new(self, *args, **kwargs) -> LoanApplication: 
        if args: 
            if len(*args) > 0: 
                if isinstance(args[0], dict):
                    return self.new_from_dict(*args)
                else:   
                    return self.new_from_params(*args,**kwargs) 
        if len(kwargs) >= 1:   
            return self.new_from_params(**kwargs)
        raise ValueError("Incorrect arguments supplied to Loans.new(...)")

    def new_from_dict(self, d: dict) -> LoanApplication: 
        if isinstance(d["applicant"], dict):
            d["applicant"] = Applicant.from_dict(d["applicant"])
        application_id = d["application_id"] if "application_id" in d else None 
        app = LoanApplication(  
            applicant=d["applicant"],
            requested_amount=d["requested_amount"],
            term_months=d["term_months"],
            purpose=d["purpose"],
            application_id=application_id
        )
        self._add_item(app) 
        return app 
    
    def new_from_params(self, 
                        applicant: Applicant, 
                        requested_amount: Decimal,
                        term_months: int, 
                        purpose: str,
                        application_id: str | None = None) -> LoanApplication:
        app = LoanApplication(
            applicant=applicant, 
            requested_amount=requested_amount,
            term_months=term_months,
            purpose=purpose,
            application_id=application_id
        )
        self._add_item(app)
        return app 
 
    def _add_item(self, item: LoanApplication) -> None:  
        if item.application_id in Loans.items: 
            raise ValueError("LoanApplication id already exists")
        Loans.items[item.application_id] = item.to_dict()
        self.save({
            "type": "Loans", 
            "id": item.application_id, 
            "data": item.to_dict()
        })
        self.emit({
            "event": "SUBMITTED",
            "id": item.application_id,
            "data": item.to_dict() 
        })
     
    def get(self, id: str) -> LoanApplication:
        if id in Loans.items: 
            item = Loans.items[id] 
            if isinstance(item, str):
                item = LoanApplication.from_json(item)
            if isinstance(item, dict):
                if "data" in item: item = item["data"]
                item = LoanApplication.from_dict(item["data"])
            return Loans.items[id]
        raise ValueError("LoanApplication not found")
    
    @overload
    def delete(self, item: LoanApplication):... 
    @overload
    def delete(self, item: str):...

    def delete(self, item: Any) -> None:
        if isinstance(item, LoanApplication):
            item = item.application_id
        self.delete_loan(item)

    def delete_loan(self, item: str):
        if item in Loans.items:  
            del Loans.items[item]
            self.update_file(Loans.items) 

    def clear(self): 
        self.clear_file()
        Loans.items = {} 
 