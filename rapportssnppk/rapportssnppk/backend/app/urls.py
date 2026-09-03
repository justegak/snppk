from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import *
r=DefaultRouter(); r.register('reports',ReportViewSet); r.register('bowls',BowlViewSet); r.register('corrections',CorrectionViewSet); r.register('geo',GeoViewSet); r.register('data',DataViewSet); r.register('audit',AuditViewSet)
urlpatterns=r.urls+[path('dashboard/',dashboard)]
