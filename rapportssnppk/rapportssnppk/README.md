# SNPPK — Pilotage & Traçabilité

Application web PWA offline-first bilingue FR/EN pour le pilotage et la traçabilité du SNPPK.

## Cible de déploiement
- Domaine : `rapportssnppk.cgwgroups.com`
- VPS : Contabo `161.97.164.142`
- Architecture compatible avec un VPS hébergeant déjà d'autres applications : le stack écoute uniquement sur `127.0.0.1:9080`.
- HTTPS : à terminer dans le reverse-proxy existant du VPS (exemple Nginx fourni).

## Stack
- Backend : Django + Django REST Framework + SimpleJWT + PostgreSQL/PostGIS
- Frontend : React + Vite + TypeScript + PWA + IndexedDB/Dexie + Leaflet
- Reverse proxy : Nginx
- Déploiement : Docker Compose

## Fonctions livrées
- RBAC 5 rôles : Super Admin, National, Régional, Superviseur, Contrôleur.
- Workflow strict des rapports : Brouillon → Soumis → Transmis au national → Validé / Renvoyé.
- Cloisonnement serveur par périmètre.
- Déclaration des bols et verrouillage après soumission.
- Demandes de correction des bols.
- Journal d'audit append-only applicatif.
- Saisie terrain offline avec file de synchronisation.
- Capture GPS automatique, mode dégradé et repli manuel.
- Carte consolidée multi-couches : Sites, Contrôles, Sensibilisation, Incidents/Alertes.
- FR/EN persistant hors ligne.
- Dashboard adapté au rôle.
- Export CSV et API de données prêtes pour PDF/Excel.
- Service Worker PWA et cache offline.
- Healthcheck et configuration Docker.

## Déploiement
1. Installer Docker et Docker Compose sur le VPS.
2. Copier ce dossier sur le VPS.
3. `cp .env.example .env` puis définir les secrets.
4. `docker compose up -d --build`
5. Créer le compte racine : `docker compose exec backend python manage.py createsuperuser`
6. Ajouter le vhost fourni dans `nginx/rapportssnppk.conf` à l'instance Nginx existante.
7. Obtenir/installer le certificat TLS avec l'outil déjà utilisé sur le VPS.
8. Tester `https://rapportssnppk.cgwgroups.com/health`.

## Important
Le GPS hors ligne est indépendant du réseau, mais la disponibilité d'une position dépend du matériel GNSS et des permissions du navigateur. Les tuiles cartographiques sont mises en cache pour les zones déjà consultées ; pour une cartographie totalement autonome dans des zones sans réseau, prévoir un paquet de tuiles MBTiles/PMTiles auto-hébergé.
