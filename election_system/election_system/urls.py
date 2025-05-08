from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Include app's URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('election.urls')),  # Including app's URLs (home and other pages)
]

# Serve static files and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])  # Serve static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve media files
