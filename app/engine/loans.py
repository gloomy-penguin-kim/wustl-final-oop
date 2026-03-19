from __future__ import annotations
from decimal import Decimal
from typing import Any, overload
from datetime import datetime, UTC

from app.persistence import JsonStore
from app.domain import LoanApplication, Applicant 
from app.audit import EmitEvent 
from .wrapper import Wrapper
 
class Loans(Wrapper, JsonStore, EmitEvent):  
    items = {} 
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        Loans.items = Loans.items | self.load_by_type()

    def register(self, item: LoanApplication) -> None:
        self._add_item(item)  
 
    @overload
    def new(self, application: dict) -> LoanApplication:...
    
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
        if isinstance(d.get("applicant"), dict):
            d["applicant"] = Applicant.from_dict(d.get("applicant"))
        application_id = d.get("application_id", None)
        app = LoanApplication(  
            applicant        = d.get("applicant"),
            requested_amount = d.get("requested_amount"),
            term_months      = d.get("term_months"),
            purpose          = d.get("purpose"),
            application_id   = application_id
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
        if id not in Loans.items:
            item = self.load_one(id)
            if item:
                Loans.items[id] = item
            else:
                raise ValueError(f"LoanApplication not found: {id}")
        item = Loans.items[id]
        if isinstance(item, str):
            item = LoanApplication.from_json(item)
        if isinstance(item, dict):
            if "data" in item: item = item.get("data")
            item = LoanApplication.from_dict(item)
        return item
    
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
            self.update_file(Loans.items) 
            del Loans.items[item]

    def clear(self): 
        self.clear_file() 
        Loans.items = {} 
 