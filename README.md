# Look@Me CMS - Sistema di Gestione Display in Vetrina

Sistema CMS completo per gestire display in vetrina con personalizzazione contenuti, integrazioni social media, calcolo sostenibilità AI e molto altro.

## 🚀 Caratteristiche Principali

- **Autenticazione JWT** - Sistema sicuro di registrazione e login
- **Dashboard CMS Completo** - Gestione branding, visibilità, social, sostenibilità, servizi e riconoscimenti
- **Integrazioni Social Media** - Instagram, Facebook, Google Maps (via BrightData), TripAdvisor (API diretta)
- **AI Sostenibilità** - Calcolo intelligente dell'indice di sostenibilità con Gemini AI
- **Preview Display** - Visualizzazione in tempo reale del display per vetrina
- **API RESTful** - Backend FastAPI con MongoDB
- **BrightData Integration** - Crawling asincrono dei dati social con job management

## 🛠️ Tech Stack

- **Frontend**: React + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI Integration**: Google Gemini (via Emergent Integrations)
- **Deployment**: Docker + Docker Compose

## 📋 Prerequisiti

- Docker Desktop installato e attivo
- Git
- (Opzionale) Node.js 18+ e Python 3.11+ per sviluppo locale

## 🚀 Setup Locale con Docker

### 1. Clona il Repository

```bash
git clone https://github.com/tuo-username/look-at-me-cms.git
cd look-at-me-cms
```

### 2. Configura le Variabili d'Ambiente

**Backend** (`backend/.env`):
```bash
cp backend/.env.example backend/.env
```

Modifica `backend/.env` e aggiungi le tue chiavi:
```env
MONGO_URL=mongodb://mongodb:27017/lookatme_cms
JWT_SECRET=tua_chiave_segreta_jwt_qui
EMERGENT_LLM_KEY=tua_chiave_emergent_llm_qui

# Opzionali - Per integrazioni real-time
GOOGLE_MAPS_API_KEY=
TRIPADVISOR_API_KEY=
FACEBOOK_ACCESS_TOKEN=
INSTAGRAM_ACCESS_TOKEN=
```

**Frontend** (`frontend/.env`):
```bash
cp frontend/.env.example frontend/.env
```

Il file `.env` del frontend:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. Avvia con Docker

```bash
docker-compose up --build
```

Attendi che tutti i servizi siano avviati:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **MongoDB**: localhost:27017

### 4. Accedi all'Applicazione

Apri il browser e vai su: **http://localhost:3000**

## 📚 Struttura del Progetto

```
look-at-me-cms/
├── backend/
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example       # Template variabili d'ambiente
│   └── Dockerfile.backend
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   └── index.js
│   ├── package.json       # Node dependencies
│   ├── yarn.lock          # Lock file dependencies
│   ├── .env.example       # Template variabili d'ambiente
│   └── Dockerfile.frontend
├── docker-compose.yml     # Orchestrazione servizi
└── README.md
```

## 🔌 API Endpoints Principali

### Autenticazione
- `POST /api/auth/register` - Registrazione nuovo utente
- `POST /api/auth/login` - Login utente
- `GET /api/auth/me` - Info utente corrente

### Configurazione Store
- `GET /api/config` - Ottieni configurazione store
- `PUT /api/config` - Aggiorna configurazione store

### Integrazioni Social
- `GET /api/integrations/google-reviews` - Recensioni Google Maps
- `GET /api/integrations/tripadvisor` - Dati TripAdvisor
- `GET /api/integrations/facebook` - Likes Facebook
- `GET /api/integrations/instagram` - Followers Instagram

### Sostenibilità AI
- `POST /api/sustainability/calculate` - Calcola indice sostenibilità

### Display Pubblico
- `GET /api/display/{user_id}` - Dati display per vetrina (pubblico)

## 🔑 Ottenere le Chiavi API

### Emergent LLM Key
1. Accedi al tuo account Emergent
2. Vai su Profilo → Universal Key
3. Copia la chiave e aggiungila a `backend/.env`

### Google Maps API
1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Abilita Places API
3. Crea credenziali API Key

### Altri Servizi
- **TripAdvisor**: [TripAdvisor Content API](https://www.tripadvisor.com/developers)
- **Facebook/Instagram**: [Meta for Developers](https://developers.facebook.com/)

## 🧪 Testing

Il progetto include test completi per backend e frontend. Controlla `test_result.md` per i dettagli dei test eseguiti.

## 📝 Note di Sviluppo

- Il backend usa **hot reload** - le modifiche ai file Python si riflettono automaticamente
- Il frontend React usa **hot reload** - le modifiche si aggiornano nel browser
- MongoDB persiste i dati in un volume Docker
- Le chiavi API sono opzionali - l'app funziona anche senza integrazioni esterne

## 🐛 Risoluzione Problemi

### Docker non si avvia
```bash
# Ferma tutti i container
docker-compose down

# Riavvia pulendo
docker-compose up --build --force-recreate
```

### Porta già in uso
```bash
# Controlla processi sulle porte
lsof -i :3000  # Frontend
lsof -i :8001  # Backend
lsof -i :27017 # MongoDB

# Termina il processo o cambia porta in docker-compose.yml
```

### Errori di dipendenze
```bash
# Ricostruisci le immagini
docker-compose build --no-cache
```

## 📄 Licenza

Questo progetto è stato creato con [Emergent.sh](https://emergent.sh)

## 🤝 Supporto

Per domande o problemi, apri un'issue su GitHub.
