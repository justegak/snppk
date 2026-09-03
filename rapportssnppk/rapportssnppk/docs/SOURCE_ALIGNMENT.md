# Alignement avec les sources

Le code reprend le cahier de prompts v7 et le classeur SNPPK : rôles hiérarchisés, workflow des rapports, déclaration verrouillée des bols, audit, modules métier, GPS offline-first, carte consolidée, FR/EN et déploiement adapté à un VPS existant.

Le classeur contient 18 feuilles : Paramètres, Sociétés, Sites, Production, Acteurs, Contrôles, Sensibilisation, Flux, Ressources, Difficultés, Actions, Alertes, Dashboard, Classement, Carte_Sites, Rapport_Mensuel et Qualité, plus README.

La couche `DataRecord` permet de couvrir les registres métier du classeur sans imposer une structure JSON fragile au schéma relationnel principal. Une évolution de production peut ensuite normaliser chaque registre en table dédiée.
