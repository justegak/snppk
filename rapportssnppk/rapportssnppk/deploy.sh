#!/bin/sh
set -e
cp -n .env.example .env || true
if grep -q 'CHANGE_ME' .env; then echo 'ERREUR: éditez .env et remplacez tous les CHANGE_ME'; exit 1; fi
docker compose up -d --build
echo 'Application démarrée sur http://127.0.0.1:9080'
