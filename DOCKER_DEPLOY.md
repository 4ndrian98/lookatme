# Look@Me CMS - Guida Deploy Docker

Questa guida ti aiuterà a fare il deploy dell'applicazione Look@Me CMS usando Docker.

## 📋 Prerequisiti

- Docker (versione 20.10 o superiore)
- Docker Compose (versione 2.0 o superiore)
- 2GB di RAM disponibile
- Porte 3000, 8001, 27017 libere

## 🚀 Quick Start (Sviluppo)

### 1. Clona o scarica il progetto

```bash
cd /app
```

### 2. Avvia tutti i servizi

```bash
docker-compose up -d
```

Questo comando avvierà:
- MongoDB (porta 27017)
- Backend FastAPI (porta 8001)
- Frontend React (porta 3000)

### 3. Verifica che tutto sia avviato

```bash
docker-compose ps
```

Dovresti vedere 3 container in stato "Up".

### 4. Accedi all'applicazione

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### 5. Visualizza i logs

```bash
# Tutti i servizi
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

## 🔧 Configurazione API Keys (Opzionale)

Per abilitare le integrazioni social media:

1. Copia il file di esempio:
```bash
cp .env.docker .env
```

2. Modifica `.env` e inserisci le tue API keys:
```bash
GOOGLE_MAPS_API_KEY=la_tua_chiave
TRIPADVISOR_API_KEY=la_tua_chiave
FACEBOOK_ACCESS_TOKEN=il_tuo_token
INSTAGRAM_ACCESS_TOKEN=il_tuo_token
```

3. Riavvia i servizi:
```bash
docker-compose down
docker-compose up -d
```

## 🏭 Deploy Produzione

### 1. Prepara le variabili d'ambiente

```bash
cp .env.prod.example .env.prod
```

Modifica `.env.prod` con:
- Password MongoDB sicure
- JWT secret forte (minimo 32 caratteri)
- Domini corretti per CORS
- URL backend pubblico

### 2. Avvia in produzione

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 3. Verifica la sicurezza

- ✅ Cambia tutte le password di default
- ✅ Usa JWT_SECRET casuale e forte
- ✅ Configura CORS solo per i tuoi domini
- ✅ Considera l'uso di HTTPS con reverse proxy (nginx/traefik)
- ✅ Abilita firewall per limitare l'accesso a MongoDB

## 📦 Comandi Utili

### Fermare i servizi
```bash
docker-compose down
```

### Fermare e rimuovere volumi (ATTENZIONE: cancella i dati)
```bash
docker-compose down -v
```

### Ricostruire le immagini
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Accedere alla shell del backend
```bash
docker exec -it lookatme-backend bash
```

### Accedere a MongoDB
```bash
docker exec -it lookatme-mongodb mongosh lookatme_cms
```

### Backup del database
```bash
docker exec lookatme-mongodb mongodump --db lookatme_cms --out /backup
docker cp lookatme-mongodb:/backup ./backup-$(date +%Y%m%d)
```

### Restore del database
```bash
docker cp ./backup-20250101 lookatme-mongodb:/backup
docker exec lookatme-mongodb mongorestore --db lookatme_cms /backup/lookatme_cms
```

## 🔍 Troubleshooting

### Il frontend non si connette al backend

1. Verifica che il backend sia in esecuzione:
```bash
curl http://localhost:8001/api/health
```

2. Controlla i logs del backend:
```bash
docker-compose logs backend
```

3. Verifica la configurazione CORS nel backend

### MongoDB non si avvia

1. Verifica che la porta 27017 sia libera:
```bash
lsof -i :27017
```

2. Controlla i logs:
```bash
docker-compose logs mongodb
```

3. Assicurati di avere spazio su disco sufficiente

### Errori di build

1. Pulisci la cache Docker:
```bash
docker system prune -a
```

2. Ricostruisci senza cache:
```bash
docker-compose build --no-cache
```

## 🌐 Deploy su Cloud

### AWS ECS / Azure Container Instances / Google Cloud Run

1. Carica le immagini su Docker Hub o registry privato:
```bash
docker tag lookatme-backend:latest yourusername/lookatme-backend:latest
docker push yourusername/lookatme-backend:latest

docker tag lookatme-frontend:latest yourusername/lookatme-frontend:latest
docker push yourusername/lookatme-frontend:latest
```

2. Configura il servizio MongoDB gestito (MongoDB Atlas, AWS DocumentDB, etc.)

3. Aggiorna le variabili d'ambiente con gli URL cloud

4. Deploy dei container usando gli strumenti specifici del cloud provider

### Docker Swarm / Kubernetes

Per deploy su cluster, converti il `docker-compose.yml` usando:
- **Swarm**: `docker stack deploy -c docker-compose.yml lookatme`
- **Kubernetes**: `kompose convert` per generare i manifest YAML

## 📊 Monitoraggio

### Verifica lo stato di salute
```bash
# Backend health
curl http://localhost:8001/api/health

# Verifica tutti i container
docker-compose ps
```

### Statistiche risorse
```bash
docker stats
```

## 🔐 Sicurezza

### Checklist Produzione

- [ ] Cambiare tutte le password di default
- [ ] Generare JWT_SECRET casuale forte
- [ ] Configurare CORS specifico (non *)
- [ ] Usare HTTPS con certificati SSL
- [ ] Limitare l'accesso a MongoDB (non esporre pubblicamente)
- [ ] Configurare backup automatici
- [ ] Abilitare logging e monitoraggio
- [ ] Implementare rate limiting
- [ ] Aggiornare regolarmente le dipendenze

## 📝 Note

- I dati MongoDB sono persistiti nel volume `mongodb_data`
- Il frontend è ottimizzato per produzione con nginx
- Il backend usa uvicorn con hot reload disabilitato in produzione
- Consulta `API_KEYS_INSTRUCTIONS.md` per dettagli sulle API keys social media

## 🆘 Supporto

Per problemi o domande:
1. Controlla i logs: `docker-compose logs`
2. Verifica il file `.env` per le configurazioni
3. Consulta la documentazione delle API: http://localhost:8001/docs