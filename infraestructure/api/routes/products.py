from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from domain.models.product import Product
from domain.ports.product_service import ProductService
from infraestructure.api.dependencies import get_product_service
from config.security import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Delete a product by ID.
    Only admins can delete products.
    """
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete products"
        )

    try:
        await product_service.delete_product(product_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {str(e)}"
        )

    return None
