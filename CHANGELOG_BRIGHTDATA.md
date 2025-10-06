# Changelog - Integrazione BrightData

## Data: 6 Ottobre 2025

### 🎯 Obiettivo
Sostituire le API dirette di Instagram, Facebook e Google Maps con **BrightData** per un crawling più affidabile e flessibile.

---

## ✨ Modifiche Implementate

### 1. Backend - Nuovi File

#### `/app/backend/brightdata_integration.py`
Nuovo modulo Python per gestire l'integrazione con BrightData:

- **Classe `BrightDataClient`**: Client per interagire con BrightData API
  - `trigger_crawl()`: Avvia job di crawling
  - `check_job_status()`: Controlla stato job
  - `get_results()`: Recupera risultati completati
  - `wait_for_completion()`: Attende completamento job

- **Parser Functions**: 
  - `parse_instagram_data()`: Estrae followers, posts
  - `parse_facebook_data()`: Estrae fans, reviews, rating
  - `parse_googlemaps_data()`: Estrae reviews count, rating

- **Helper Function**: 
  - `get_social_data_via_brightdata()`: Funzione high-level per crawling

### 2. Backend - Modifiche a `server.py`

#### Variabili d'Ambiente
```python
BRIGHTDATA_API_TOKEN = os.environ.get('BRIGHTDATA_API_TOKEN', '')
```

#### Modello `StoreConfig` Aggiornato
Nuovi campi per URL completi:
```python
instagram_url: Optional[str] = None
facebook_url: Optional[str] = None  
google_maps_url: Optional[str] = None
```

#### Endpoint Aggiornati
Modificati per usare BrightData invece di API dirette:

- `GET /api/social/instagram-data?profile_url=...`
  - Prima: Usava Instagram Graph API
  - Ora: Crea job BrightData, ritorna `job_id`

- `GET /api/social/facebook-likes?page_url=...`
  - Prima: Usava Facebook Graph API
  - Ora: Crea job BrightData, ritorna `job_id`

- `GET /api/social/google-reviews?place_url=...`
  - Prima: Usava Google Places API
  - Ora: Crea job BrightData, ritorna `job_id`

#### Nuovi Endpoint

**Job Management:**
- `GET /api/brightdata/job-status/{job_id}` - Controlla stato job
- `GET /api/brightdata/job-results/{job_id}` - Recupera risultati
- `GET /api/brightdata/my-jobs` - Lista tutti i job utente

**Bulk Operations:**
- `POST /api/brightdata/refresh-all-social` - Aggiorna tutti i dati social in una volta

### 3. Configurazione

#### `backend/.env.example`
```env
# BrightData Integration (Required for Instagram, Facebook, Google Maps)
BRIGHTDATA_API_TOKEN=your_brightdata_api_token_here

# TripAdvisor Direct API (Optional)
TRIPADVISOR_API_KEY=your_tripadvisor_api_key_here

# Legacy Direct API Keys (Not needed if using BrightData)
# GOOGLE_MAPS_API_KEY=
# FACEBOOK_ACCESS_TOKEN=
# INSTAGRAM_ACCESS_TOKEN=
```

### 4. Documentazione

#### Nuovi File
- `BRIGHTDATA_SETUP.md` - Guida completa integrazione BrightData
- `CHANGELOG_BRIGHTDATA.md` - Questo file
- `SETUP_LOCALE.md` - Aggiornato con istruzioni BrightData

#### File Aggiornati
- `README.md` - Menziona BrightData nelle features
- `.gitignore` - Corretto per permettere `.env.example`

---

## 🔄 Differenze Principali

### Prima (API Dirette)
```javascript
// Chiamata immediata, dati istantanei
GET /api/social/instagram-data?username=user
→ {followers: 1234, posts: 56}
```

### Dopo (BrightData)
```javascript
// Step 1: Avvia crawl
GET /api/social/instagram-data?profile_url=https://...
→ {job_id: "abc123", status: "running"}

// Step 2: Controlla stato (polling)
GET /api/brightdata/job-status/abc123
→ {status: "ready", progress: 100}

// Step 3: Recupera risultati
GET /api/brightdata/job-results/abc123
→ {data: {followers: 1234, posts: 56}}
```

---

## 📊 Dataset IDs Configurati

```python
dataset_ids = {
    "instagram": "gd_l7q7dkf244hwjntr0",
    "facebook": "gd_lvhf8tq8ky28b3tbz",    
    "googlemaps": "gd_l7q7dkf244hwjku40"
}
```

> ⚠️ **Nota**: Se hai dataset IDs diversi, modificali in `brightdata_integration.py`

---

## 🗄️ Database

### Nuova Collection: `brightdata_jobs`

Struttura documento:
```javascript
{
  user_id: "uuid",
  job_id: "snapshot_id_from_brightdata",
  platform: "instagram" | "facebook" | "googlemaps",
  url: "https://...",
  status: "running" | "completed" | "failed",
  results: {...},  // Popolato al completamento
  created_at: "ISO timestamp",
  completed_at: "ISO timestamp"
}
```

---

## ⚙️ Frontend - Modifiche Necessarie

### Componente Social Data (da implementare)

```javascript
// 1. Cambia parametri degli endpoint
// Prima:
fetch(`/api/social/instagram-data?username=${username}`)

// Dopo:
fetch(`/api/social/instagram-data?profile_url=${encodeURIComponent(fullUrl)}`)

// 2. Gestisci risposta asincrona
const response = await fetch(...);
const data = await response.json();

if (data.job_id) {
  // Avvia polling
  pollJobStatus(data.job_id, 'instagram');
}

// 3. Implementa polling
const pollJobStatus = async (jobId, platform) => {
  const checkStatus = async () => {
    const res = await fetch(`/api/brightdata/job-status/${jobId}`);
    const status = await res.json();
    
    if (status.status === 'ready') {
      fetchResults(jobId);
    } else {
      setTimeout(checkStatus, 30000); // Ricontrolla dopo 30s
    }
  };
  checkStatus();
};

// 4. Recupera e mostra risultati
const fetchResults = async (jobId) => {
  const res = await fetch(`/api/brightdata/job-results/${jobId}`);
  const result = await res.json();
  updateUI(result.data);
};
```

### UI/UX Considerations

1. **Indicatori di caricamento**: Mostra "Aggiornamento in corso..." durante crawling
2. **Tempi stimati**: "I dati saranno pronti tra ~60 secondi"
3. **Notifiche**: Avvisa utente quando i dati sono pronti
4. **Cache**: Mostra dati vecchi mentre carica nuovi
5. **Errori**: Gestisci fallimenti con retry

---

## 🧪 Testing

### Test Endpoint BrightData

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' \
  | jq -r '.token')

# 2. Avvia crawl Instagram
JOB=$(curl -X GET "http://localhost:8001/api/social/instagram-data?profile_url=https://www.instagram.com/cats_of_world_/" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.job_id')

echo "Job ID: $JOB"

# 3. Controlla stato
curl -X GET "http://localhost:8001/api/brightdata/job-status/$JOB" \
  -H "Authorization: Bearer $TOKEN"

# 4. Recupera risultati (dopo ~60s)
curl -X GET "http://localhost:8001/api/brightdata/job-results/$JOB" \
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚠️ Breaking Changes

### API Endpoint Parameters

**Instagram:**
- ❌ Prima: `?username=user`
- ✅ Ora: `?profile_url=https://www.instagram.com/user/`

**Facebook:**
- ❌ Prima: `?page_id=123456`
- ✅ Ora: `?page_url=https://www.facebook.com/page/`

**Google Maps:**
- ❌ Prima: `?place_id=ChIJ...`
- ✅ Ora: `?place_url=https://www.google.com/maps/place/...`

### Response Format

**Prima (Sincrono):**
```json
{
  "followers": 1234,
  "posts": 56
}
```

**Ora (Asincrono):**
```json
{
  "job_id": "abc123",
  "status": "running",
  "message": "Crawl job started"
}
```

---

## 🚀 Deployment

### 1. Aggiorna Backend
```bash
cd /app/backend
pip install httpx  # Se non già installato
```

### 2. Configura Token
Aggiungi `BRIGHTDATA_API_TOKEN` in `backend/.env`

### 3. Riavvia Servizi
```bash
sudo supervisorctl restart backend
```

### 4. Verifica Health
```bash
curl http://localhost:8001/api/health
```

---

## 🔐 Sicurezza

- ✅ Token BrightData memorizzato solo su backend
- ✅ Tutti gli endpoint richiedono autenticazione JWT
- ✅ Utenti vedono solo i propri job
- ✅ Rate limiting gestito da BrightData

---

## 📈 Benefici

### Vantaggi BrightData vs API Dirette

| Aspetto | API Dirette | BrightData |
|---------|-------------|-----------|
| **Setup** | Token OAuth complessi | 1 API token |
| **Rate Limits** | Restrittivi | Più flessibili |
| **Manutenzione** | Aggiornamenti frequenti | Gestita da BD |
| **Affidabilità** | Dipende da FB/IG | Proxy globali |
| **Costo** | Gratis (con limiti) | Paghi per crawl |

### Trade-offs

**Svantaggi:**
- ⏱️ Aggiornamento non istantaneo (~60s)
- 💰 Costo per crawl (vs gratuito)
- 🔄 Polling necessario (vs response diretta)

**Quando usare BrightData:**
- ✅ Dati non in tempo reale (es: display vetrina)
- ✅ Volumi medio-alti
- ✅ Stabilità prioritaria

**Quando NON usare:**
- ❌ Real-time updates critici
- ❌ Budget limitato
- ❌ Pochi utenti

---

## 📝 TODO

### Frontend (Da Implementare)
- [ ] Aggiornare form configurazione per URL completi
- [ ] Implementare polling automatico per job
- [ ] UI per stato crawling ("Aggiornamento in corso...")
- [ ] Gestione errori crawling
- [ ] Cache dati precedenti durante refresh

### Backend (Opzionale)
- [ ] Webhook per notifiche job completati
- [ ] Scheduler automatico (crawl giornaliero)
- [ ] Dashboard admin per monitorare job
- [ ] Retry automatico per job falliti

### Testing
- [ ] Unit tests per `brightdata_integration.py`
- [ ] Integration tests endpoint BrightData
- [ ] Load testing con job concorrenti

---

## 🆘 Troubleshooting

### Error: "BrightData API token not configured"
**Soluzione**: Aggiungi `BRIGHTDATA_API_TOKEN` in `backend/.env` e riavvia backend

### Job rimane "running" per sempre
**Cause possibili**:
1. URL non valido
2. Dataset ID errato
3. Token BrightData scaduto

**Soluzione**: Controlla logs backend, verifica token su BrightData dashboard

### Results vuoti
**Cause**:
1. Account social privato
2. URL non pubblicamente accessibile
3. Anti-bot measures

**Soluzione**: Verifica che il profilo sia pubblico

---

## 📞 Supporto

- **BrightData**: https://brightdata.com/support
- **Look@Me CMS**: Apri issue su GitHub
- **Logs**: `tail -f /var/log/supervisor/backend.err.log`

---

## ✅ Checklist Migrazione

- [x] Creato modulo `brightdata_integration.py`
- [x] Aggiornati endpoint social in `server.py`
- [x] Aggiunti endpoint job management
- [x] Aggiornato `StoreConfig` model
- [x] Creato `.env.example` aggiornato
- [x] Documentazione completa (`BRIGHTDATA_SETUP.md`)
- [x] Changelog dettagliato
- [x] README aggiornato
- [ ] Frontend aggiornato (TODO)
- [ ] Testing completo (TODO)

---

**Versione**: 1.0  
**Autore**: Emergent Agent E1  
**Data**: 6 Ottobre 2025
