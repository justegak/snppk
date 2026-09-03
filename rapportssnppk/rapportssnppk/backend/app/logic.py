from decimal import Decimal
from .models import Setting,BowlDeclaration

DEFAULTS={'rendement_par_bol':'0.100','seuil_sanction_niveau_1':'10','seuil_sanction_niveau_2':'25','seuil_sanction_niveau_3':'50','seuil_alerte_quota':'0.80'}

def get_setting(key):
    try: return Decimal(str(Setting.objects.get(key=key).value))
    except Setting.DoesNotExist: return Decimal(DEFAULTS[key])

def recompute_bowl(bowl):
    """Rejoue les règles quota/dette/sanction du classeur SNPPK (feuille Sociétés) pour un bol déclaré."""
    rendement=get_setting('rendement_par_bol')
    seuil1=get_setting('seuil_sanction_niveau_1'); seuil2=get_setting('seuil_sanction_niveau_2'); seuil3=get_setting('seuil_sanction_niveau_3')
    seuil_alerte=get_setting('seuil_alerte_quota')
    bowl.quota_kg=(bowl.number or Decimal('0'))*rendement
    bowl.realization_rate=(bowl.gold_extracted_kg/bowl.quota_kg) if bowl.quota_kg>0 else Decimal('0')
    bowl.monthly_debt_kg=max(bowl.quota_kg-bowl.gold_extracted_kg,Decimal('0'))
    prev=BowlDeclaration.objects.filter(company_id=bowl.company_id,month__lt=bowl.month).exclude(pk=bowl.pk).order_by('-month').first()
    prev_cumulative=prev.cumulative_debt_kg if prev else Decimal('0')
    bowl.cumulative_debt_kg=max(prev_cumulative+bowl.monthly_debt_kg-bowl.debt_adjustment_kg,Decimal('0'))
    if bowl.cumulative_debt_kg>=seuil3: bowl.sanction_level='NIVEAU_3'
    elif bowl.cumulative_debt_kg>=seuil2: bowl.sanction_level='NIVEAU_2'
    elif bowl.cumulative_debt_kg>=seuil1: bowl.sanction_level='NIVEAU_1'
    else: bowl.sanction_level=''
    if bowl.realization_rate<seuil_alerte: bowl.quota_status='SOUS_QUOTA'
    elif bowl.realization_rate<1: bowl.quota_status='A_SURVEILLER'
    else: bowl.quota_status='QUOTA_ATTEINT'
    return bowl

def cascade_recompute(bowl):
    """Recalcule le bol puis répercute en cascade sur les mois suivants de la même société (la dette cumulée est chaînée mois après mois)."""
    recompute_bowl(bowl); bowl.save()
    for nxt in BowlDeclaration.objects.filter(company_id=bowl.company_id,month__gt=bowl.month).order_by('month'):
        recompute_bowl(nxt); nxt.save()
    return bowl
