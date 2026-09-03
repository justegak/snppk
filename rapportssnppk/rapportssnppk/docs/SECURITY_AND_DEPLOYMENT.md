# Déploiement sécurisé

## VPS multi-applications
Le projet n'occupe pas les ports 80/443 : le frontend Docker expose uniquement `127.0.0.1:9080`. Il peut donc cohabiter avec les applications déjà présentes sur le Contabo.

## Nginx existant
Ajoutez le bloc de `nginx/rapportssnppk.conf`, adaptez les chemins TLS, puis `nginx -t && systemctl reload nginx`.

## Sauvegarde
Exemple quotidien :
`docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > backup-$(date +%F).sql.gz`
Conservez plusieurs générations hors du VPS et testez la restauration.

## Sécurité
- Secrets uniquement dans `.env`, jamais dans Git.
- HTTPS obligatoire en production.
- RBAC côté serveur, pas uniquement côté client.
- Journal fonctionnel dédié aux actions sensibles.
- Le compte Super Admin doit utiliser un mot de passe fort et, idéalement, un MFA via le reverse proxy/SSO.
