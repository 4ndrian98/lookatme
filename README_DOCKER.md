# 🪟 Look@Me CMS - Guida Rapida Docker

Sistema CMS completo per gestire display intelligenti in vetrina con integrazioni social media, AI per sostenibilità, e interfaccia di personalizzazione no-code.

## ✨ Caratteristiche

- 🔐 **Autenticazione JWT** - Sistema sicuro di login e registrazione
- 🎨 **Editor Visuale** - Interfaccia drag-and-drop per personalizzare il display
- 📱 **Integrazioni Social** - Google Maps, TripAdvisor, Facebook, Instagram
- 🌱 **AI Sostenibilità** - Calcolo automatico indice sostenibilità con Gemini AI
- 👁️ **Anteprima Live** - Visualizza in tempo reale come apparirà il display
- ⚙️ **Gestione Servizi** - Configura amenities e servizi aggiuntivi
- 🏆 **Certificazioni** - Aggiungi badge e riconoscimenti

## 🚀 Avvio Rapido (5 minuti)

### 1. Prerequisiti
- Docker Desktop installato
- 2GB RAM disponibile
- Porte 3000, 8001, 27017 libere

### 2. Avvia l'applicazione

**Linux/Mac:**
```bash
./start-docker.sh
```

**Windows (PowerShell):**
```powershell
docker-compose up -d
```

### 3. Accedi
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/docs

### 4. Primo utilizzo
1. Clicca su "Registrati"
2. Compila i campi (username, email, nome attività, password)
3. Accedi al CMS
4. Inizia a personalizzare il tuo display!

## 🔧 Configurazione API Keys Social Media

Le API social sono **opzionali**. L'applicazione funziona senza, ma per dati reali:

1. Copia il file di configurazione:
```bash
cp .env.docker .env
```

2. Apri `.env` e inserisci le tue chiavi:
```env
GOOGLE_MAPS_API_KEY=la_tua_chiave_qui
TRIPADVISOR_API_KEY=la_tua_chiave_qui
FACEBOOK_ACCESS_TOKEN=il_tuo_token_qui
INSTAGRAM_ACCESS_TOKEN=il_tuo_token_qui
```

3. Riavvia:
```bash
docker-compose restart backend
```

📖 **Guida completa** per ottenere le chiavi: vedi `API_KEYS_INSTRUCTIONS.md`

## 📦 Struttura del Progetto

```
look@me-cms/
├── backend/                 # FastAPI backend
│   ├── server.py           # API principale
│   └── requirements.txt    # Dipendenze Python
├── frontend/               # React frontend
│   └── src/
│       ├── App.js         # Componente principale
│       └── App.css        # Stili
├── docker-compose.yml      # Configurazione Docker
├── Dockerfile.backend      # Build backend
├── Dockerfile.frontend     # Build frontend
├── start-docker.sh         # Script avvio
└── DOCKER_DEPLOY.md        # Documentazione completa
```

## 🛠️ Comandi Utili

### Visualizza logs
```bash
# Tutti i servizi
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### Ferma i servizi
```bash
./stop-docker.sh
# oppure
docker-compose down
```

### Riavvia un servizio
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Pulisci e riparti da zero
```bash
docker-compose down -v  # ⚠️ Cancella anche i dati!
docker-compose up -d --build
```

## 🏭 Deploy in Produzione

Per deploy in produzione con password sicure e HTTPS:

1. Copia configurazione produzione:
```bash
cp .env.prod.example .env.prod
```

2. Modifica `.env.prod` con password sicure e domini reali

3. Avvia in modalità produzione:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

📖 **Guida completa**: vedi `DOCKER_DEPLOY.md`

## 🎯 Casi d'Uso

### Per Negozi
- Mostra recensioni Google e TripAdvisor in vetrina
- Evidenzia i tuoi like Facebook e follower Instagram
- Comunica orari, servizi e certificazioni

### Per Ristoranti
- Display dinamico con menu del giorno
- Mostra il tuo indice di sostenibilità
- Certificazioni alimentari e premi

### Per Attività Sostenibili
- Calcola il tuo indice di sostenibilità con AI
- Comunica impegno ambientale e sociale
- Mostra certificazioni eco-friendly

## 🔍 Troubleshooting

### Il backend non parte
```bash
# Controlla i logs
docker-compose logs backend

# Verifica MongoDB
docker-compose ps mongodb
```

### Il frontend mostra errori
```bash
# Verifica che il backend sia attivo
curl http://localhost:8001/api/health

# Controlla i logs
docker-compose logs frontend
```

### Problemi con MongoDB
```bash
# Riavvia MongoDB
docker-compose restart mongodb

# Se persiste, ricrea il volume
docker-compose down -v
docker-compose up -d
```

## 📊 Architettura

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │─────▶│  Frontend   │─────▶│   Backend   │
│             │      │   (React)   │      │  (FastAPI)  │
└─────────────┘      └─────────────┘      └──────┬──────┘
                            │                     │
                            │                     ▼
                            │              ┌─────────────┐
                            │              │   MongoDB   │
                            │              └─────────────┘
                            ▼
                     ┌─────────────┐
                     │  External   │
                     │  APIs       │
                     │  (Social/AI)│
                     └─────────────┘
```

## 🔐 Sicurezza

### Sviluppo
- ✅ CORS aperto (*)
- ✅ JWT con secret di default
- ✅ MongoDB senza autenticazione

### Produzione (docker-compose.prod.yml)
- 🔒 CORS limitato ai tuoi domini
- 🔒 JWT secret forte e casuale
- 🔒 MongoDB con username/password
- 🔒 HTTPS consigliato

## 📈 Performance

- **Frontend**: Ottimizzato con build React production + nginx
- **Backend**: Uvicorn con worker multipli
- **Database**: Indici MongoDB per query veloci
- **Cache**: Headers cache per asset statici

## 🤝 Supporto

Per assistenza dettagliata:
1. Consulta `DOCKER_DEPLOY.md` per documentazione completa
2. Controlla `API_KEYS_INSTRUCTIONS.md` per le API social
3. Vedi i logs: `docker-compose logs`

## 📝 Note Tecniche

- **Stack**: React + FastAPI + MongoDB
- **Autenticazione**: JWT con bcrypt/pbkdf2
- **AI**: Gemini 2.0 Flash via emergentintegrations
- **Social APIs**: REST integration con error handling
- **Persistenza**: Volume Docker per MongoDB

## 🎉 Pronto!

Ora puoi:
1. Registrare un utente: http://localhost:3000
2. Personalizzare il display
3. Vedere l'anteprima
4. Pubblicare!

**Buon lavoro con Look@Me CMS! 🚀**
