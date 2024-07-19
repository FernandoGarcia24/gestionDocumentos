"""
URL configuration for gestion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from registro import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signin),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('list/', views.document_list, name='document_list'),
    path('upload/', views.document_upload, name='document_upload'),
    path('edit/<int:pk>/', views.document_edit, name='document_edit'),
    path('delete/<int:pk>/', views.document_delete, name='document_delete'),
    path('preview/<int:document_id>/', views.document_preview, name='document_preview'),
    path('approve/<int:document_id>/', views.approve_document, name='approve_document'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
