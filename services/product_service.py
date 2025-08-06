import time
import uuid
import json
from typing import Optional, List, Dict, Any
from database.redis_connection import redis_conn
from models.productmodels import (
    Product, ProductCreate, ProductUpdate, ProductSearchFilter,
    ProductCategory
)


class ProductService:
    """Servicio para manejar operaciones de productos"""
    
    def __init__(self):
        self.redis = redis_conn
    
    def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        """Crear un nuevo producto"""
        try:
            product_id = str(uuid.uuid4())
            product_key = f"product:{product_id}"
            
            product = {
                "id": product_id,
                "nombre": product_data.nombre,
                "descripcion": product_data.descripcion,
                "precio": product_data.precio,
                "categoria": product_data.categoria.value,
                "imagen_url": product_data.imagen_url,
                "disponible": product_data.disponible,
                "tiempo_preparacion": product_data.tiempo_preparacion,
                "created_at": str(int(time.time())),
                "updated_at": None
            }
            
            # Guardar producto
            success = self.redis.set_data(product_key, product)
            if not success:
                return {
                    "success": False,
                    "message": "Error al guardar el producto",
                    "product": None
                }
            
            # Indexar por categoría
            category_products_key = f"category_products:{product_data.categoria.value}"
            existing_category_products = self.redis.get_data(category_products_key) or []
            existing_category_products.append(product_id)
            self.redis.set_data(category_products_key, existing_category_products)
            
            # Agregar a lista general de productos
            all_products_key = "all_products"
            all_products = self.redis.get_data(all_products_key) or []
            all_products.append(product_id)
            self.redis.set_data(all_products_key, all_products)
            
            return {
                "success": True,
                "message": "Producto creado exitosamente",
                "product": product
            }
            
        except Exception as e:
            print(f"❌ Error creando producto: {e}")
            return {
                "success": False,
                "message": "Error interno del servidor",
                "product": None
            }
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Obtener producto por ID"""
        try:
            product_key = f"product:{product_id}"
            return self.redis.get_data(product_key)
        except Exception as e:
            print(f"❌ Error obteniendo producto: {e}")
            return None
    
    def update_product(self, product_id: str, product_data: ProductUpdate) -> Dict[str, Any]:
        """Actualizar un producto"""
        try:
            product = self.get_product(product_id)
            if not product:
                return {
                    "success": False,
                    "message": "Producto no encontrado",
                    "product": None
                }
            
            # Actualizar solo los campos proporcionados
            update_data = product_data.model_dump(exclude_unset=True)
            
            # Si se cambia la categoría, actualizar índices
            old_category = product.get("categoria")
            
            for field, value in update_data.items():
                if field == "categoria" and value:
                    product[field] = value.value
                else:
                    product[field] = value
            
            product["updated_at"] = str(int(time.time()))
            
            # Guardar producto actualizado
            product_key = f"product:{product_id}"
            success = self.redis.set_data(product_key, product)
            
            if not success:
                return {
                    "success": False,
                    "message": "Error al actualizar el producto",
                    "product": None
                }
            
            # Si cambió la categoría, actualizar índices
            if "categoria" in update_data and update_data["categoria"]:
                new_category = update_data["categoria"].value
                if old_category != new_category:
                    # Remover de categoría anterior
                    old_category_key = f"category_products:{old_category}"
                    old_category_products = self.redis.get_data(old_category_key) or []
                    if product_id in old_category_products:
                        old_category_products.remove(product_id)
                        self.redis.set_data(old_category_key, old_category_products)
                    
                    # Agregar a nueva categoría
                    new_category_key = f"category_products:{new_category}"
                    new_category_products = self.redis.get_data(new_category_key) or []
                    if product_id not in new_category_products:
                        new_category_products.append(product_id)
                        self.redis.set_data(new_category_key, new_category_products)
            
            return {
                "success": True,
                "message": "Producto actualizado exitosamente",
                "product": product
            }
            
        except Exception as e:
            print(f"❌ Error actualizando producto: {e}")
            return {
                "success": False,
                "message": "Error interno del servidor",
                "product": None
            }
    
    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """Eliminar un producto"""
        try:
            product = self.get_product(product_id)
            if not product:
                return {
                    "success": False,
                    "message": "Producto no encontrado"
                }
            
            categoria = product["categoria"]
            
            # Remover de productos por categoría
            category_products_key = f"category_products:{categoria}"
            category_products = self.redis.get_data(category_products_key) or []
            if product_id in category_products:
                category_products.remove(product_id)
                self.redis.set_data(category_products_key, category_products)
            
            # Remover de lista general
            all_products_key = "all_products"
            all_products = self.redis.get_data(all_products_key) or []
            if product_id in all_products:
                all_products.remove(product_id)
                self.redis.set_data(all_products_key, all_products)
            
            # Eliminar el producto
            product_key = f"product:{product_id}"
            success = self.redis.delete_data(product_key)
            
            if not success:
                return {
                    "success": False,
                    "message": "Error al eliminar el producto"
                }
            
            return {
                "success": True,
                "message": "Producto eliminado exitosamente"
            }
            
        except Exception as e:
            print(f"❌ Error eliminando producto: {e}")
            return {
                "success": False,
                "message": "Error interno del servidor"
            }
    
    def get_all_products(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Obtener todos los productos"""
        try:
            all_products_key = "all_products"
            product_ids = self.redis.get_data(all_products_key) or []
            
            # Paginación
            start = offset
            end = offset + limit
            paginated_ids = product_ids[start:end]
            
            products = []
            for product_id in paginated_ids:
                product = self.get_product(product_id)
                if product:
                    products.append(product)
            
            # Ordenar por fecha de creación (más recientes primero)
            products.sort(key=lambda x: x.get("created_at", "0"), reverse=True)
            
            return products
            
        except Exception as e:
            print(f"❌ Error obteniendo todos los productos: {e}")
            return []
    
    def search_products(self, filters: ProductSearchFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Buscar productos con filtros"""
        try:
            products = []
            
            # Si hay filtro por categoría, usar índice de categoría
            if filters.categoria:
                category_products_key = f"category_products:{filters.categoria.value}"
                product_ids = self.redis.get_data(category_products_key) or []
                
                for product_id in product_ids:
                    product = self.get_product(product_id)
                    if product and self._matches_filters(product, filters):
                        products.append(product)
            
            # Búsqueda general
            else:
                all_products_key = "all_products"
                product_ids = self.redis.get_data(all_products_key) or []
                
                for product_id in product_ids:
                    product = self.get_product(product_id)
                    if product and self._matches_filters(product, filters):
                        products.append(product)
            
            # Ordenar por fecha de creación (más recientes primero)
            products.sort(key=lambda x: x.get("created_at", "0"), reverse=True)
            
            # Paginación
            start = offset
            end = offset + limit
            return products[start:end]
            
        except Exception as e:
            print(f"❌ Error buscando productos: {e}")
            return []
    
    def _matches_filters(self, product: Dict, filters: ProductSearchFilter) -> bool:
        """Verificar si un producto coincide con los filtros"""
        try:
            # Filtro por categoría
            if filters.categoria and product.get("categoria") != filters.categoria.value:
                return False
            
            # Filtro por precio mínimo
            if filters.precio_min is not None and product.get("precio", 0) < filters.precio_min:
                return False
            
            # Filtro por precio máximo
            if filters.precio_max is not None and product.get("precio", 0) > filters.precio_max:
                return False
            
            # Filtro por disponibilidad
            if filters.disponible is not None and product.get("disponible") != filters.disponible:
                return False
            
            # Filtro por término de búsqueda
            if filters.search_term:
                search_term = filters.search_term.lower()
                nombre = product.get("nombre", "").lower()
                descripcion = product.get("descripcion", "").lower()
                
                if search_term not in nombre and search_term not in descripcion:
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando filtros: {e}")
            return False
    
    def get_products_by_category(self, category: ProductCategory, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Obtener productos por categoría"""
        try:
            category_products_key = f"category_products:{category.value}"
            product_ids = self.redis.get_data(category_products_key) or []
            
            # Paginación
            start = offset
            end = offset + limit
            paginated_ids = product_ids[start:end]
            
            products = []
            for product_id in paginated_ids:
                product = self.get_product(product_id)
                if product:
                    products.append(product)
            
            # Ordenar por fecha de creación (más recientes primero)
            products.sort(key=lambda x: x.get("created_at", "0"), reverse=True)
            
            return products
            
        except Exception as e:
            print(f"❌ Error obteniendo productos por categoría: {e}")
            return []
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de productos"""
        try:
            # Contar productos totales
            all_products_key = "all_products"
            all_product_ids = self.redis.get_data(all_products_key) or []
            total_products = len(all_product_ids)
            
            # Contar productos disponibles
            available_products = 0
            products_by_category = {}
            
            for product_id in all_product_ids:
                product = self.get_product(product_id)
                if product:
                    if product.get("disponible", True):
                        available_products += 1
                    
                    category = product.get("categoria", "otros")
                    products_by_category[category] = products_by_category.get(category, 0) + 1
            
            return {
                "total_products": total_products,
                "available_products": available_products,
                "unavailable_products": total_products - available_products,
                "products_by_category": products_by_category
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {
                "total_products": 0,
                "available_products": 0,
                "unavailable_products": 0,
                "products_by_category": {}
            }


# Instancia global del servicio
product_service = ProductService()
