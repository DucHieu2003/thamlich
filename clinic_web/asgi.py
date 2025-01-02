import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import web_core.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_web.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            web_core.routing.websocket_urlpatterns
        )
    ),
})
