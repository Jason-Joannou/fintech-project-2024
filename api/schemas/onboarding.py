from pydantic import BaseModel, Field


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
    stokvel_id: int = Field(..., example=123)
    stokvel_name: str = Field(..., example="John's Soccer Stokvel") #unique constraint here
    ILP_wallet: str = Field(..., example="/johns_stokvel")
    MOMO_wallet: str = Field(..., example="MOMO10255")
    total_members: int = Field(..., example=15)
    min_contributing_amount: float = Field(..., example=100.50)
    max_number_of_contributors: int = Field(..., example=20)
    Total_contributions: float = Field(..., example=153800)
    created_at: str = Field(..., example="2024-10-01 00:00:00")
    updated_at: str = Field(..., example="2024-10-01 00:00:00")
