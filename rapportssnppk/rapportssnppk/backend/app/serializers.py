from rest_framework import serializers
from .models import *
class ReportSerializer(serializers.ModelSerializer):
    class Meta: model=Report; fields='__all__'; read_only_fields=['region','department','arrondissement','brigade','status','submitted_at','submitted_by','national_edit_history']
class BowlSerializer(serializers.ModelSerializer):
    class Meta: model=BowlDeclaration; fields='__all__'; read_only_fields=['locked','declared_by','modified_by_national','modification_reason','history','quota_kg','realization_rate','monthly_debt_kg','cumulative_debt_kg','sanction_level','quota_status']
class CorrectionSerializer(serializers.ModelSerializer):
    class Meta: model=CorrectionRequest; fields='__all__'; read_only_fields=['requester','status','treated_by','treated_at']
class GeoSerializer(serializers.ModelSerializer):
    class Meta: model=GeoRecord; fields='__all__'; read_only_fields=['created_by']
class DataSerializer(serializers.ModelSerializer):
    class Meta: model=DataRecord; fields='__all__'; read_only_fields=['created_by']
class AuditSerializer(serializers.ModelSerializer):
    class Meta: model=AuditLog; fields='__all__'
