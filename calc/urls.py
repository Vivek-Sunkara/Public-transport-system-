from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    pakka_local_view,
    register,
    loginPage,
    logoutPage,
    page1_view,
    reports_view,
    users_view,
    settings_view,
)

# URL patterns
urlpatterns = [
    path('', pakka_local_view, name='pakka_local'),  # Home page
    path('register/', register, name='register'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutPage, name='logout'),
    path('page1/', page1_view, name='page1'),  # Path for Home
    path('reports/', reports_view, name='reports'),  # Path for Reports
    path('users/', users_view, name='users'),  # Path for Users
    path('settings/', settings_view, name='settings'),  # Path for Settings
]

# Add this to serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
