from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets,status
from rest_framework.decorators import action,api_view,permission_classes
from rest_framework.response import Response
from .models import *
from .serializers import *
from .permissions import HasRole,role,in_scope
from .logic import cascade_recompute

def health(request): return JsonResponse({'status':'ok','service':'rapportssnppk','time':timezone.now().isoformat()})
def audit(user,action,entity,entity_id='',before=None,after=None,reason=''):
    return AuditLog.objects.create(actor=user,action=action,entity=entity,entity_id=str(entity_id),before=before,after=after,reason=reason)
class ScopedMixin:
    scope_prefix=''
    def get_queryset(self):
        qs=super().get_queryset(); p=self.request.user.profile; pre=self.scope_prefix
        if p.role=='SUPER_ADMIN' or p.role=='NATIONAL': return qs
        if p.role=='REGIONAL': return qs.filter(**{pre+'region':p.region})
        if p.role in ('SUPERVISEUR','CONTROLEUR'): return qs.filter(**{pre+'brigade':p.brigade,pre+'arrondissement':p.arrondissement})
        return qs.none()
class ReportViewSet(ScopedMixin,viewsets.ModelViewSet):
    queryset=Report.objects.all(); serializer_class=ReportSerializer; permission_classes=[HasRole]
    def perform_create(self,serializer):
        if role(self.request)!='SUPERVISEUR': from rest_framework.exceptions import PermissionDenied; raise PermissionDenied()
        p=self.request.user.profile; obj=serializer.save(submitted_by=self.request.user,region=p.region,department=p.departement,arrondissement=p.arrondissement,brigade=p.brigade); audit(self.request.user,'CREATE','Report',obj.id,after=serializer.data)
    def update(self,request,*args,**kwargs):
        obj=self.get_object(); r=role(request)
        if r not in ('NATIONAL','SUPER_ADMIN'): return Response({'detail':'Modification directe réservée au National/Super Admin.'},status=403)
        if obj.status=='VALIDATED' and r!='SUPER_ADMIN': return Response({'detail':'Rapport validé : modification réservée au Super Admin.'},status=403)
        if obj.status not in ('TRANSMITTED','VALIDATED') and r!='SUPER_ADMIN': return Response({'detail':'Rapport non accessible à ce stade.'},status=403)
        reason=request.data.get('_reason','')
        if r=='NATIONAL' and not reason: return Response({'detail':'Motif obligatoire.'},status=400)
        before=ReportSerializer(obj).data; resp=super().update(request,*args,**kwargs); audit(request.user,'DIRECT_EDIT','Report',obj.id,before=before,after=resp.data,reason=reason); return resp
    @action(detail=True,methods=['post'])
    def submit(self,request,pk=None):
        obj=self.get_object()
        if role(request)!='SUPERVISEUR' or obj.status!='DRAFT': return Response({'detail':'Action interdite.'},status=403)
        if not obj.bowls.exists(): return Response({'detail':'Déclaration des bols incomplète ou non validée.'},status=400)
        obj.status='SUBMITTED'; obj.submitted_at=timezone.now(); obj.save(); obj.bowls.update(locked=True); audit(request.user,'SUBMIT','Report',obj.id); return Response(ReportSerializer(obj).data)
    @action(detail=True,methods=['post'])
    def transmit(self,request,pk=None):
        obj=self.get_object()
        if role(request)!='REGIONAL' or obj.status!='SUBMITTED': return Response({'detail':'Action interdite.'},status=403)
        obj.status='TRANSMITTED'; obj.save(); audit(request.user,'TRANSMIT','Report',obj.id); return Response(ReportSerializer(obj).data)
    @action(detail=True,methods=['post'])
    def return_correction(self,request,pk=None):
        obj=self.get_object(); r=role(request)
        if r not in ('REGIONAL','NATIONAL') or not request.data.get('reason'): return Response({'detail':'Motif obligatoire/action interdite.'},status=400)
        if r=='REGIONAL' and obj.status!='SUBMITTED': return Response({'detail':'Action interdite.'},status=403)
        if r=='NATIONAL' and obj.status!='TRANSMITTED': return Response({'detail':'Action interdite.'},status=403)
        obj.status='RETURNED'; obj.save(); audit(request.user,'RETURN','Report',obj.id,reason=request.data['reason']); return Response(ReportSerializer(obj).data)
    @action(detail=True,methods=['post'])
    def validate(self,request,pk=None):
        obj=self.get_object()
        if role(request)!='NATIONAL' or obj.status!='TRANSMITTED': return Response({'detail':'Action interdite.'},status=403)
        obj.status='VALIDATED'; obj.save(); audit(request.user,'VALIDATE','Report',obj.id); return Response(ReportSerializer(obj).data)
class BowlViewSet(ScopedMixin,viewsets.ModelViewSet):
    queryset=BowlDeclaration.objects.select_related('report'); serializer_class=BowlSerializer; permission_classes=[HasRole]; scope_prefix='report__'
    def perform_create(self,serializer):
        if role(self.request) not in ('SUPERVISEUR','CONTROLEUR'): from rest_framework.exceptions import PermissionDenied; raise PermissionDenied()
        obj=serializer.save(declared_by=self.request.user); cascade_recompute(obj); audit(self.request.user,'CREATE','BowlDeclaration',obj.id,after=BowlSerializer(obj).data)
    def update(self,request,*args,**kwargs):
        obj=self.get_object(); r=role(request)
        if obj.locked and r not in ('NATIONAL','SUPER_ADMIN'): return Response({'detail':'Déclaration verrouillée.'},status=403)
        if obj.locked and r=='NATIONAL' and not request.data.get('_reason'): return Response({'detail':'Motif obligatoire.'},status=400)
        before=BowlSerializer(obj).data; resp=super().update(request,*args,**kwargs)
        obj.refresh_from_db()
        if r=='NATIONAL': obj.modified_by_national=request.user; obj.modification_reason=request.data.get('_reason','')
        cascade_recompute(obj); resp.data=BowlSerializer(obj).data
        if r=='NATIONAL': audit(request.user,'NATIONAL_BOWL_EDIT','BowlDeclaration',obj.id,before=before,after=resp.data,reason=request.data.get('_reason',''))
        return resp
class CorrectionViewSet(ScopedMixin,viewsets.ModelViewSet):
    queryset=CorrectionRequest.objects.select_related('bowl'); serializer_class=CorrectionSerializer; permission_classes=[HasRole]; scope_prefix='bowl__report__'
    def perform_create(self,serializer):
        if role(self.request)!='SUPERVISEUR': from rest_framework.exceptions import PermissionDenied; raise PermissionDenied()
        obj=serializer.save(requester=self.request.user); audit(self.request.user,'CREATE','CorrectionRequest',obj.id,after=serializer.data)
    @action(detail=True,methods=['post'])
    def treat(self,request,pk=None):
        if role(request)!='NATIONAL': return Response({'detail':'Réservé au National.'},status=403)
        obj=self.get_object(); bowl=obj.bowl; reason=request.data.get('reason',''); decision=request.data.get('decision')
        if not reason or decision not in ('approve','reject'): return Response({'detail':'Décision et motif obligatoires.'},status=400)
        obj.status='TREATED' if decision=='approve' else 'REJECTED'; obj.treated_by=request.user; obj.treatment_reason=reason; obj.treated_at=timezone.now(); obj.save()
        if decision=='approve': bowl.history.append({'at':timezone.now().isoformat(),'from':str(bowl.number),'to':str(obj.proposed_number),'by':request.user.username,'reason':reason}); bowl.number=obj.proposed_number; bowl.modified_by_national=request.user; bowl.modification_reason=reason; cascade_recompute(bowl)
        audit(request.user,'TREAT_BOWL_CORRECTION','CorrectionRequest',obj.id,reason=reason); return Response(CorrectionSerializer(obj).data)
class GeoViewSet(ScopedMixin,viewsets.ModelViewSet):
    queryset=GeoRecord.objects.all(); serializer_class=GeoSerializer; permission_classes=[HasRole]
    def perform_create(self,serializer): obj=serializer.save(created_by=self.request.user); audit(self.request.user,'CREATE_GEO','GeoRecord',obj.id,after=serializer.data)
class DataViewSet(ScopedMixin,viewsets.ModelViewSet):
    queryset=DataRecord.objects.all(); serializer_class=DataSerializer; permission_classes=[HasRole]
    def perform_create(self,serializer):
        p=self.request.user.profile; obj=serializer.save(created_by=self.request.user,region=p.region,department=p.departement,arrondissement=p.arrondissement,brigade=p.brigade); audit(self.request.user,'CREATE_DATA',obj.module,obj.id,after=serializer.data)
class AuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=AuditLog.objects.all(); serializer_class=AuditSerializer; permission_classes=[HasRole]
    def get_queryset(self):
        qs=super().get_queryset(); r=role(self.request)
        if r in ('SUPER_ADMIN','NATIONAL'): return qs
        return qs.filter(actor=self.request.user)
@api_view(['GET'])
@permission_classes([HasRole])
def dashboard(request):
    p=request.user.profile; qs=Report.objects.all()
    if p.role=='REGIONAL': qs=qs.filter(region=p.region)
    elif p.role in ('SUPERVISEUR','CONTROLEUR'): qs=qs.filter(brigade=p.brigade,arrondissement=p.arrondissement)
    elif p.role=='NATIONAL': qs=qs.filter(status__in=['TRANSMITTED','VALIDATED'])
    geo=GeoRecord.objects.filter(region=p.region) if p.role=='REGIONAL' else GeoRecord.objects.all() if p.role in ('SUPER_ADMIN','NATIONAL') else GeoRecord.objects.filter(arrondissement=p.arrondissement)
    return Response({'role':p.role,'reports':{'total':qs.count(),'draft':qs.filter(status='DRAFT').count(),'submitted':qs.filter(status='SUBMITTED').count(),'transmitted':qs.filter(status='TRANSMITTED').count(),'validated':qs.filter(status='VALIDATED').count(),'returned':qs.filter(status='RETURNED').count()},'geo':GeoSerializer(geo,many=True).data})
