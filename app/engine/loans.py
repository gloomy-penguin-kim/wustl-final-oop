from __future__ import annotations
from decimal import Decimal
from typing import Any, overload
from datetime import datetime, UTC

from app.audit.hash_chain import HashChain
from app.persistence import JsonStore
from app.domain import LoanApplication, Applicant 
from app.audit import EmitEvent
from app.settings import Config
from .wrapper import Wrapper


class Loans(Wrapper, JsonStore, EmitEvent, HashChain):

    items = dict()

    def __init__(self, filename: str, **kwargs):
        super().__init__(filename=filename, **kwargs)
        self.filename = filename 
        Loans.items = Loans.items | self.load_by_type() 
    
    def register(self, application: LoanApplication):
        self._add_item(application)
        return application
 
    @overload
    def new(self, application: LoanApplication) -> LoanApplication: ...
 
    @overload
    def new(self, application: dict) -> LoanApplication: ...
    
    @overload
    def new(self, 
            applicant: Applicant, 
            requested_amount: Decimal, 
            term_months: int, 
            purpose: str,
            application_id: str | None = None) -> LoanApplication: ...
 
    def new(self, *args, **kwargs) -> LoanApplication: 
        if args: 
            if len(args) > 0: 
                if isinstance(args[0], dict):
                    return self.new_from_dict(*args)
                if isinstance(args[0], LoanApplication):
                    self._add_item(*args)
                    return args[0]
                else:   
                    return self.new_from_params(*args,**kwargs) 
        if len(kwargs) >= 1:   
            return self.new_from_params(**kwargs)
        raise ValueError("Incorrect arguments supplied to Loans.new(...)")

    # TODO: Clean this up and check for default values or None it all 
    def new_from_dict(self, d: dict) -> LoanApplication: 
        if d.get("applicant") == None:
            a = d["application_id"]
            raise ValueError(f"Applicant is missing on LoanApplication {a}")
        if isinstance(d.get("applicant"), dict):
            d["applicant"] = Applicant.from_dict(d.get("applicant"))
        application_id = d.get("application_id", None)
        app = LoanApplication(  
            applicant=d.get("applicant"),
            requested_amount=d.get("requested_amount", Decimal(0)),
            term_months=d.get("term_months", 0),
            purpose=d.get("purpose", ""),
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

        assert item is not None

        Loans.items[item.application_id] = item.to_dict()

        self.save({
            "type": "Loans", 
            "id": item.application_id, 
            "data": item.to_dict()
        })
        self.chain_event({
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
            if "data" in item:
                item = item.get("data")
            item = LoanApplication.from_dict(item)
        return item
    
    @overload
    def delete(self, application: LoanApplication): ...
    @overload
    def delete(self, item: str): ...

    def delete(self, application: Any) -> None:
        if isinstance(application, LoanApplication):
            application = application.application_id
        self.delete_loan(application)

    def delete_loan(self, application: str):
        if application in Loans.items:  
            self.update_file(Loans.items) 
            del Loans.items[application]

    def clear(self): 
        self.clear_file() 
        Loans.items = dict()
 