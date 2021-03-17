"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from news_agency.views import user_login_in, user_log_out, post_story, get_story, delete_story

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', user_login_in),
    path('api/logout/', user_log_out),
    path('api/poststory/', post_story),
    path('api/getstories/', get_story),
    path('api/deletestory/', delete_story)
]
