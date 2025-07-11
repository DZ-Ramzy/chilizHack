# Guide de Test - Intégration TheSportsDB

## 🚀 Démarrage Rapide

### 1. Lancer le serveur
```bash
cd agent_system
# Si vous avez un environnement virtuel configuré :
source venv/bin/activate
python -m src

# Sinon, installer globalement (non recommandé) :
pip install --break-system-packages -r requirements.txt
python -m src
```

Le serveur démarre sur `http://localhost:8001`

### 2. Tester l'intégration

#### Option A: Script automatique
```bash
./test_api.sh
```

#### Option B: Tests manuels avec curl

**Test 1: Recherche d'équipe**
```bash
curl "http://localhost:8001/api/sync/test-team/Arsenal"
```

**Test 2: Événements d'une équipe**
```bash
curl "http://localhost:8001/api/sync/test-events/Arsenal"
```

**Test 3: Synchronisation améliorée des équipes**
```bash
curl -X POST "http://localhost:8001/api/sync/teams/enhanced"
```

**Test 4: Synchronisation des événements**
```bash
curl -X POST "http://localhost:8001/api/sync/events"
```

**Test 5: Synchronisation complète + génération de quêtes**
```bash
curl -X POST "http://localhost:8001/api/sync/full"
```

**Test 6: Statut du scheduler**
```bash
curl "http://localhost:8001/api/sync/scheduler/status"
```

## 🎯 Workflow de Test Complet

### Étape 1: Initialiser les données
```bash
# Via l'API
curl -X POST "http://localhost:8001/api/sync/teams"
```

### Étape 2: Mapper les équipes avec TheSportsDB
```bash
# Mapping automatique amélioré
curl -X POST "http://localhost:8001/api/sync/teams/enhanced"
```

### Étape 3: Synchroniser les événements
```bash
# Récupérer les vrais matchs depuis TheSportsDB
curl -X POST "http://localhost:8001/api/sync/events"
```

### Étape 4: Déclencher la génération de quêtes
```bash
# Workflow complet avec génération automatique de quêtes
curl -X POST "http://localhost:8001/api/sync/full"
```

### Étape 5: Vérifier les résultats
```bash
# Voir les événements créés
curl "http://localhost:8001/api/events"

# Voir les quêtes générées
curl "http://localhost:8001/api/quests"
```

## 🔧 Test d'une équipe spécifique

Pour tester avec une équipe particulière :

```bash
# Test PSG
curl "http://localhost:8001/api/sync/test-team/PSG"
curl "http://localhost:8001/api/sync/test-events/PSG"

# Synchroniser les événements de PSG uniquement
curl -X POST -H "Content-Type: application/json" \
  -d '{"team_name": "PSG", "trigger_quests": true}' \
  "http://localhost:8001/api/sync/team"
```

## 📊 Endpoints Disponibles

### Synchronisation
- `POST /api/sync/teams` - Sync basique des équipes
- `POST /api/sync/teams/enhanced` - Sync avancé avec fuzzy matching
- `POST /api/sync/events` - Sync des événements
- `POST /api/sync/full` - Sync complet + génération de quêtes
- `POST /api/sync/team` - Sync d'une équipe spécifique

### Scheduler
- `GET /api/sync/scheduler/status` - Statut du scheduler
- `POST /api/sync/scheduler/start` - Démarrer le scheduler
- `POST /api/sync/scheduler/stop` - Arrêter le scheduler
- `POST /api/sync/scheduler/trigger` - Déclencher une sync manuelle

### Test/Debug
- `GET /api/sync/test-team/{team_name}` - Tester la recherche d'équipe
- `GET /api/sync/test-events/{team_name}` - Tester les événements d'une équipe

### Workflow (génération de quêtes)
- `POST /api/workflow/trigger-event` - Déclencher une quête pour un événement
- `POST /api/workflow/trigger-event-sync` - Version synchrone

## 🎲 Scénarios de Test

### Scénario 1: Nouvelle équipe
1. Ajouter une nouvelle équipe en DB
2. Lancer le mapping amélioré
3. Vérifier que l'équipe est trouvée dans TheSportsDB
4. Synchroniser ses événements

### Scénario 2: Événement avec les deux équipes existantes
1. S'assurer que PSG et Real Madrid sont mappées
2. Créer un événement "PSG vs Real Madrid"
3. Vérifier qu'une quête individuelle + clash est générée

### Scénario 3: Événement avec une seule équipe
1. Créer un événement avec une équipe non-mappée
2. Vérifier qu'une seule quête individuelle est générée

## 🐛 Debugging

### Logs
Les logs sont affichés dans la console du serveur. Cherchez :
- `✅` pour les succès
- `❌` pour les erreurs
- `⚠️` pour les avertissements

### Vérification manuelle
```bash
# Voir les équipes en DB
curl "http://localhost:8001/api/teams"

# Voir les événements en DB  
curl "http://localhost:8001/api/events"

# Voir les quêtes générées
curl "http://localhost:8001/api/quests"
```

### Base de données
La DB SQLite est dans `sports_quest.db` - vous pouvez l'inspecter avec :
```bash
sqlite3 sports_quest.db ".tables"
sqlite3 sports_quest.db "SELECT * FROM teams LIMIT 5;"
sqlite3 sports_quest.db "SELECT * FROM sports_events LIMIT 5;"
```

## ✅ Critères de Succès

L'intégration fonctionne si :

1. **Mapping des équipes** : Les équipes de la DB sont associées aux IDs TheSportsDB
2. **Récupération d'événements** : Les vrais matchs sont importés depuis l'API
3. **Génération de quêtes** : Les agents créent automatiquement des quêtes basées sur les nouveaux événements
4. **Scheduler** : Le système vérifie périodiquement les nouveaux matchs
5. **Workflow complet** : Nouveaux matchs → Nouvelles quêtes distribuées aux communautés

## 🔄 Automatisation

Une fois testé manuellement, le scheduler s'occupe automatiquement de :
- Vérifier les nouveaux matchs toutes les 5 minutes (configurable)
- Mapper les nouvelles équipes
- Créer les événements en DB
- Déclencher la génération de quêtes via les agents

C'est exactement ce qui était demandé : **les quêtes sont maintenant créées automatiquement basées sur les vrais événements scrapés via l'API TheSportsDB** ! 🎉