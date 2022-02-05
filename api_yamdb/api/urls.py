from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, signup, token

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', token, name='token')
]
