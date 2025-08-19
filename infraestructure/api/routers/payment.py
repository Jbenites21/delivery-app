from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(prefix="/payment", tags=["payment"])

class Item(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    
class PaymentRequest(BaseModel):
    items: List[Item]
    total_amount: float
    
class PaymentResponse(BaseModel):
    message: str
    status: str
    transaction_id: str

@router.post("/process-payment", response_model=PaymentResponse)
def process_payment(request: PaymentRequest):
    """
    Simula el procesamiento de un pago con una API externa.
    """
    # 💡 Lógica de simulación
    if request.total_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto total debe ser mayor a cero."
        )

    # Simula un pago exitoso
    transaction_id = "txn_" + str(hash(str(request.items) + str(request.total_amount)))
    return PaymentResponse(
        message="Pago simulado exitosamente.",
        status="completed",
        transaction_id=transaction_id
    )