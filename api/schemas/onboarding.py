from pydantic import BaseModel, Field
from typing import Optional


class OnboardUserSchema(BaseModel):
    """
    docstring
    """

    name: str = Field(..., example="John")
    surname: str = Field(..., example="Doe")
    cellphone_number: str = Field(..., example="1234567890")
    id_number: str = Field(..., example="ID123456")
    wallet_id: str = Field("TestWaller", example="WalletABC")

class RegisterStokvelSchema(BaseModel):
    """
    docstring
    """
    stokvel_id: Optional[int] = Field(None, example=123)
    stokvel_name: str = Field(..., example="John's Soccer Stokvel") #unique constraint here
    ILP_wallet: Optional[str] = Field(None, example="/johns_stokvel")
    MOMO_wallet: Optional[str] = Field(None, example="MOMO10255")
    total_members: Optional[int] = Field(None, example=15)
    min_contributing_amount: float = Field(..., example=100.50)
    max_number_of_contributors: int = Field(..., example=20)
    Total_contributions: Optional[float] = Field(None, example=153800)
    start_date: str = Field(..., example="2024-10-01 00:00:00")
    end_date: str = Field(..., example="2024-10-01 00:00:00")
    payout_frequency_int: int = Field(..., example=1),
    payout_frequency_period: str = Field(..., example="day")
    created_at: Optional[str] = Field(None, example="2024-10-01 00:00:00")
    updated_at: Optional[str] = Field(None, example="2024-10-01 00:00:00")
    requesting_number: str = Field(..., example="1234567890")


class JoinStokvelSchema(BaseModel):
    """
    docstring
    """
    requesting_number: str = Field(..., example="1234567890")
    stokvel_name: str = Field(..., example="John's Soccer Stokvel") #unique constraint here
    stokvel_id: int = Field(None, example=123)

class UpdateUser(BaseModel):
    """
    docstring
    """
    