from pydantic import BaseModel, Field


class OnboardUserSchema(BaseModel):
    name: str = Field(..., example="John")
    surname: str = Field(..., example="Doe")
    cellphone_number: str = Field(..., example="1234567890")
    id_number: str = Field(..., example="ID123456")
    wallet_id: str = Field("TestWaller", example="WalletABC")
