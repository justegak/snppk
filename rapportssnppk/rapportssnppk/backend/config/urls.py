from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from app.views import health
urlpatterns=[path('admin/',admin.site.urls),path('api/token/',TokenObtainPairView.as_view()),path('api/token/refresh/',TokenRefreshView.as_view()),path('api/',include('app.urls')),path('health',health)]
