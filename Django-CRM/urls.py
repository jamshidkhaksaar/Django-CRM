from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),# Your existing URL patterns
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include((debug_toolbar.urls, 'debug_toolbar'), namespace='djdt')),
    ] + urlpatterns
    urlpatterns += [
        path('test/', views.test_view, name='test-view'),
    ]
