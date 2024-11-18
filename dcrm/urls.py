#from django.contrib import admin
from baton.autodiscover import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('website.urls')),
    
]
