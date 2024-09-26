from pydantic import BaseModel, Field
from typing import Optional


class UpdateUserSchema(BaseModel):
    """
    docstring
    """
    name: Optional[str] = Field(None, example="John")
    surname: Optional[str] = Field(None, example="Doe")
    cellphone_number: Optional[str] = Field(None, example="1234567890")
    id_number: Optional[str] = Field(None, example="ID123456")
    wallet_id: Optional[str] = Field("TestWallet", example="WalletABC")

class UpdateStokvelSchema(BaseModel):
    """
    docstring
    """
    stokvel_id: Optional[int] = Field(None, example=123)
    stokvel_name: Optional[str] = Field(None, example="John's Soccer Stokvel")  # unique constraint here
    ILP_wallet: Optional[str] = Field(None, example="/johns_stokvel")
    MOMO_wallet: Optional[str] = Field(None, example="MOMO10255")
    total_members: Optional[int] = Field(None, example=15)
    min_contributing_amount: Optional[float] = Field(None, example=100.50)
    max_number_of_contributors: Optional[int] = Field(None, example=20)
    Total_contributions: Optional[float] = Field(None, example=153800)
    start_date: Optional[str] = Field(None, example="2024-10-01 00:00:00")
    end_date: Optional[str] = Field(None, example="2024-10-01 00:00:00")
    payout_frequency_int: Optional[int] = Field(None, example=1)
    payout_frequency_period: Optional[str] = Field(None, example="day")
    created_at: Optional[str] = Field(None, example="2024-10-01 00:00:00")
    updated_at: Optional[str] = Field(None, example="2024-10-01 00:00:00")
    requesting_number: Optional[int] = Field(None, example=1)

    