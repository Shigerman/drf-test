from django.urls import include, path
from rest_framework import routers
from backend.app import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'items', views.ItemViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register),
    path('login/', views.login),
    path('send/', views.send),
    path('get/', views.get),
    path('api-auth/', include('rest_framework.urls',
        namespace='rest_framework'))
]
