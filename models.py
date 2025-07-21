from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReceiptData(BaseModel):
    filename: str
    vendor: str
    date: datetime
    amount: float
    category: Optional[str] = None
    currency: Optional[str] = "₹"

class SearchQuery(BaseModel):
    vendor: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
