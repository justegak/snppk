from django.contrib import admin
from .models import *
admin.site.register([Profile,Setting,Report,BowlDeclaration,CorrectionRequest,GeoRecord,AuditLog,DataRecord])
