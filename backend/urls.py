from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from backend.app import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'items', views.ItemViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('registration/', views.register_user),
    path('login/', views.login),
    path('send/', views.send_item_to_user),
    path('get/', views.get_item_from_user),
    path('items/', views.get_item_list_for_user),
    path('items/new/', views.create_item),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    path('admin/', admin.site.urls),
]
