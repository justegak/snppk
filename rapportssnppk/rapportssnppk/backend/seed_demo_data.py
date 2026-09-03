"""Peuple la base de développement locale avec des données réalistes (contexte Cameroun).
Usage : DJANGO_SETTINGS_MODULE=dev_settings python seed_demo_data.py
"""
import os,django,json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dev_settings')
django.setup()
from datetime import datetime,timezone as tz
from django.contrib.auth.models import User
from app.models import Profile,DataRecord
from rest_framework.test import APIClient

PASSWORD='Snppk@2026'

USERS=[
    dict(username='admin.snppk',first='Paul',last='Ngo Ndjock',role='SUPER_ADMIN',region='',dept='',arr='',brigade=''),
    dict(username='national.tchoua',first='Marie',last='Tchoua',role='NATIONAL',region='',dept='',arr='',brigade=''),
    dict(username='regional.centre',first='Jean',last='Eyenga',role='REGIONAL',region='Centre',dept='',arr='',brigade=''),
    dict(username='regional.littoral',first='Sophie',last='Mbarga',role='REGIONAL',region='Littoral',dept='',arr='',brigade=''),
    dict(username='superviseur.yde1',first='Alain',last='Nguemo',role='SUPERVISEUR',region='Centre',dept='Mfoundi',arr='Yaoundé I',brigade='Brigade Yaoundé-Centre'),
    dict(username='superviseur.dla1',first='Christelle',last='Fouda',role='SUPERVISEUR',region='Littoral',dept='Wouri',arr='Douala I',brigade='Brigade Douala-Port'),
    dict(username='controleur.yde1',first='Serge',last='Belinga',role='CONTROLEUR',region='Centre',dept='Mfoundi',arr='Yaoundé I',brigade='Brigade Yaoundé-Centre'),
    dict(username='controleur.dla1',first='Aïcha',last='Mendo',role='CONTROLEUR',region='Littoral',dept='Wouri',arr='Douala I',brigade='Brigade Douala-Port'),
]

def mkuser(u):
    user,_=User.objects.get_or_create(username=u['username'],defaults=dict(first_name=u['first'],last_name=u['last'],email=u['username']+'@snppk.cm'))
    user.first_name=u['first']; user.last_name=u['last']; user.email=u['username']+'@snppk.cm'; user.set_password(PASSWORD); user.save()
    Profile.objects.update_or_create(user=user,defaults=dict(role=u['role'],region=u['region'],departement=u['dept'],arrondissement=u['arr'],brigade=u['brigade'],language='fr'))
    return user

users={u['username']:mkuser(u) for u in USERS}
print('Comptes créés :',len(users))

def client_for(username):
    c=APIClient()
    r=c.post('/api/token/',{'username':username,'password':PASSWORD},format='json')
    assert r.status_code==200,(username,r.content)
    c.credentials(HTTP_AUTHORIZATION='Bearer '+r.json()['access'])
    return c

clients={u:client_for(u) for u in users}

def create_report(sup_username,month):
    c=clients[sup_username]
    r=c.post('/api/reports/',{'month':month},format='json')
    assert r.status_code==201,r.content
    return r.json()['id']

def add_bowl(username,report_id,month,company_id,company_name,number,site_reference='',gold_extracted_kg=0,debt_adjustment_kg=0,observation=''):
    c=clients[username]
    r=c.post('/api/bowls/',{'report':report_id,'company_id':company_id,'company_name':company_name,'site_reference':site_reference,'month':month,'number':str(number),'gold_extracted_kg':str(gold_extracted_kg),'debt_adjustment_kg':str(debt_adjustment_kg),'observation':observation},format='json')
    assert r.status_code==201,r.content
    return r.json()['id']

def submit(sup_username,report_id):
    r=clients[sup_username].post(f'/api/reports/{report_id}/submit/')
    assert r.status_code==200,r.content

def transmit(reg_username,report_id):
    r=clients[reg_username].post(f'/api/reports/{report_id}/transmit/')
    assert r.status_code==200,r.content

def validate(nat_username,report_id):
    r=clients[nat_username].post(f'/api/reports/{report_id}/validate/')
    assert r.status_code==200,r.content

def return_correction(username,report_id,reason):
    r=clients[username].post(f'/api/reports/{report_id}/return_correction/',{'reason':reason},format='json')
    assert r.status_code==200,r.content

def geo(username,type_,ref,title,region,dept,arr,lat,lon,acc,source,captured_at):
    r=clients[username].post('/api/geo/',{'type':type_,'reference':ref,'title':title,'region':region,'department':dept,'arrondissement':arr,'latitude':str(lat),'longitude':str(lon),'accuracy_m':str(acc),'source_position':source,'captured_at':captured_at},format='json')
    assert r.status_code==201,r.content
    return r.json()['id']

now=lambda:datetime.now(tz.utc).isoformat()

# --- Yaoundé (Centre) : cycle complet sur plusieurs mois, avec quotas atteints et sociétés en dette ---
rid_yde_06=create_report('superviseur.yde1','2026-06')
add_bowl('superviseur.yde1',rid_yde_06,'2026-06','COOP-YDE-01','Coopérative Agricole de Nkolbisson',132.50,'SITE-YDE-NKOLBISSON',13.50,0,'Quota atteint, production régulière.')
add_bowl('controleur.yde1',rid_yde_06,'2026-06','COOP-YDE-02','Groupement Sainte Thérèse',97.00,'SITE-YDE-NKOLBISSON',9.80,0,'Conforme au quota.')
submit('superviseur.yde1',rid_yde_06)
transmit('regional.centre',rid_yde_06)
validate('national.tchoua',rid_yde_06)

rid_yde_07=create_report('superviseur.yde1','2026-07')
b_yde_07=add_bowl('superviseur.yde1',rid_yde_07,'2026-07','COOP-YDE-01','Coopérative Agricole de Nkolbisson',145.00,'SITE-YDE-NKOLBISSON',9.00,0,'Baisse de production signalée (panne de pompe).')
add_bowl('controleur.yde1',rid_yde_07,'2026-07','COOP-YDE-03','Union des Producteurs de Yaoundé',60.25,'SITE-YDE-NKOLBISSON',6.50,0,'Quota atteint.')
submit('superviseur.yde1',rid_yde_07)
transmit('regional.centre',rid_yde_07)

rid_yde_08=create_report('superviseur.yde1','2026-08')
add_bowl('superviseur.yde1',rid_yde_08,'2026-08','COOP-YDE-01','Coopérative Agricole de Nkolbisson',110.00,'SITE-YDE-NKOLBISSON',4.00,0,'Production toujours en deçà du quota, deuxième mois consécutif.')
submit('superviseur.yde1',rid_yde_08)

rid_yde_09=create_report('superviseur.yde1','2026-09')
add_bowl('superviseur.yde1',rid_yde_09,'2026-09','COOP-YDE-02','Groupement Sainte Thérèse',54.00,'SITE-YDE-NKOLBISSON',1.00,0,'Ralentissement saisonnier.')

# --- Douala (Littoral) : inclut un renvoi pour correction et une société sous quota ---
rid_dla_07=create_report('superviseur.dla1','2026-07')
add_bowl('superviseur.dla1',rid_dla_07,'2026-07','COOP-DLA-01','Coopérative du Wouri',88.00,'SITE-DLA-PORT',3.00,0,'Sous quota, matériel en panne une partie du mois.')
add_bowl('controleur.dla1',rid_dla_07,'2026-07','COOP-DLA-02','Groupement du Port',73.50,'SITE-DLA-PORT',1.00,0,'Chiffres à vérifier — écart signalé par le contrôleur.')
submit('superviseur.dla1',rid_dla_07)
return_correction('regional.littoral',rid_dla_07,'Chiffres du bol COOP-DLA-02 incohérents avec le registre terrain, merci de vérifier.')

rid_dla_08=create_report('superviseur.dla1','2026-08')
add_bowl('superviseur.dla1',rid_dla_08,'2026-08','COOP-DLA-01','Coopérative du Wouri',102.00,'SITE-DLA-PORT',2.00,0,'Dette cumulée en hausse, deuxième mois sous quota.')
submit('superviseur.dla1',rid_dla_08)
transmit('regional.littoral',rid_dla_08)
validate('national.tchoua',rid_dla_08)

rid_dla_09=create_report('superviseur.dla1','2026-09')
add_bowl('superviseur.dla1',rid_dla_09,'2026-09','COOP-DLA-03','Coopérative de Bonabéri',65.00,'SITE-DLA-PORT',6.60,0,'Quota atteint.')

print('Rapports créés (cycle Brouillon → Soumis → Transmis → Validé/Renvoyé).')

# --- Demande de correction sur un bol verrouillé (rapport 2026-07 Yaoundé, transmis) ---
c=clients['superviseur.yde1']
r=c.post('/api/corrections/',{'bowl':b_yde_07,'proposed_number':'150.00','reason':'Recomptage terrain effectué le 28/07, écart de 5 bols identifié.'},format='json')
assert r.status_code==201,r.content
correction_id=r.json()['id']
r=clients['national.tchoua'].post(f'/api/corrections/{correction_id}/treat/',{'decision':'approve','reason':'Recomptage validé après vérification du registre.'},format='json')
assert r.status_code==200,r.content
print('Demande de correction traitée.')

# --- Points géolocalisés (sites, contrôles, sensibilisation, incident) ---
geo('superviseur.yde1','SITE','SITE-YDE-NKOLBISSON','Site de collecte de Nkolbisson','Centre','Mfoundi','Yaoundé I',3.8712,11.4680,8.5,'GPS auto',now())
geo('controleur.yde1','CONTROL','CTRL-YDE-2026-09-01','Contrôle terrain — marché de Nkolbisson','Centre','Mfoundi','Yaoundé I',3.8695,11.4702,12.0,'GPS auto',now())
geo('superviseur.yde1','INCIDENT','INC-YDE-2026-09-01','Signalement — accès difficile site secondaire','Centre','Mfoundi','Yaoundé I',3.8801,11.4599,25.0,'GPS auto dégradé',now())
geo('superviseur.dla1','SITE','SITE-DLA-PORT','Site de collecte du Port de Douala','Littoral','Wouri','Douala I',4.0483,9.7043,6.0,'GPS auto',now())
geo('controleur.dla1','SENSIBILISATION','SENS-DLA-2026-09-01','Campagne de sensibilisation — Bonabéri','Littoral','Wouri','Douala I',4.0721,9.6534,10.0,'GPS auto',now())
print('Points géolocalisés créés.')

# --- Registres métier (classeur SNPPK) ---
DataRecord.objects.get_or_create(module='SOCIETES',region='Centre',department='Mfoundi',arrondissement='Yaoundé I',brigade='Brigade Yaoundé-Centre',month='2026-09',
    data={'nom':'Coopérative Agricole de Nkolbisson','statut':'Active','date_agrement':'2021-03-12'},created_by=users['superviseur.yde1'])
DataRecord.objects.get_or_create(module='PRODUCTION',region='Littoral',department='Wouri',arrondissement='Douala I',brigade='Brigade Douala-Port',month='2026-08',
    data={'volume_estime_t':42.3,'unite':'tonnes','observation':'Hausse saisonnière'},created_by=users['superviseur.dla1'])
print('Registres métier créés.')

print()
print('=== Comptes de démonstration (mot de passe unique) ===')
print(f'Mot de passe : {PASSWORD}')
for u in USERS:
    print(f"- {u['username']:20s} {u['role']:12s} {u['first']} {u['last']}")
