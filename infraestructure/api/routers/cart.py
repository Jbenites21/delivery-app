from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from pydantic import BaseModel
import requests
from infraestructure.db.repositories.product_repo import get_db
from sqlalchemy.orm import Session
from infraestructure.services.product import ProductService as ProductServiceImpl # Asegúrate de la importación correcta

router = APIRouter(prefix="/cart", tags=["cart"])

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CartItem]

@router.post("/checkout")
def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    """
    Procesa la compra del carrito llamando a la API de pago.
    """
    product_service = ProductServiceImpl(db) # Aquí necesitas ajustar tu servicio si no está disponible directamente
    
    total_amount = 0
    payment_items = []
    
    # Valida y calcula el total del carrito
    for item in request.items:
        product = product_service.get_product_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {item.product_id} no encontrado."
            )
        total_amount += product.precio * item.quantity
        payment_items.append({"product_id": item.product_id, "quantity": item.quantity})

    # Llama a la API de pago simulada
    payment_payload = {
        "items": payment_items,
        "total_amount": total_amount
    }
    
    # 💡 En un proyecto real, aquí llamarías a una API externa (ej. Stripe.com)
    # Por ahora, usamos una llamada interna para simular
    response = requests.post(
        "http://localhost:8000/payment/process-payment",
        json=payment_payload
    )

    if response.status_code == 200:
        return {"message": "Compra procesada exitosamente.", "total": total_amount, "payment_response": response.json()}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json().get("detail", "Error en el procesamiento del pago.")
        )