from rest_framework.permissions import BasePermission
class HasRole(BasePermission):
    def has_permission(self,request,view): return request.user.is_authenticated and hasattr(request.user,'profile')
def role(request): return request.user.profile.role
def in_scope(request,obj):
    p=request.user.profile
    if p.role in ('SUPER_ADMIN','NATIONAL'): return True
    vals=[getattr(obj,k,'') for k in ('region','department','arrondissement','brigade')]
    if p.role=='REGIONAL': return not p.region or vals[0]==p.region
    if p.role in ('SUPERVISEUR','CONTROLEUR'): return (not p.brigade or vals[3]==p.brigade) and (not p.arrondissement or vals[2]==p.arrondissement)
    return False
