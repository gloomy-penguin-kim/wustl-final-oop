from decimal import Decimal

from app.audit import EmitEvent, HashChain
from app.domain import LoanApplication, Applicant
from app.persistence import JsonCrud

hc = HashChain("tests/output/test_audit.jsonl")
hc.clear()
ee = EmitEvent("tests/output/test_events.jsonl")
ee.clear()
jc = JsonCrud("tests/output/test_persistence.jsonl")
jc.clear()
app = LoanApplication(
    applicant=Applicant(
        name="Alice",
        annual_income=Decimal("0"),
        monthly_debt=Decimal("1500"),
        credit_score=700,
        employment_status="EMPLOYED"
    ),
    requested_amount=Decimal("15000"),
    term_months=36,
    purpose="car"
)
app.submit()

app2 = app.copy()
assert app2.created_at == app.created_at
assert app2.submitted_at == app.submitted_at
assert app2.isequal(app)
