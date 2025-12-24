from .auth import router as auth_router
from .admin import router as admin_router
from .categories import router as categories_router
from .products import router as products_router
from .orders import router as orders_router
from .settings import router as settings_router

__all__ = [
    "auth_router",
    "admin_router",
    "categories_router",
    "products_router",
    "orders_router",
    "settings_router"
]
