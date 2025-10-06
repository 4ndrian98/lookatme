# BrightData Integration - Look@Me CMS

## Panoramica

Look@Me CMS utilizza **BrightData** per raccogliere dati da:
- **Instagram**: followers count, posts count
- **Facebook**: fans count, reviews count, rating  
- **Google Maps**: reviews count, rating

**TripAdvisor** utilizza ancora l'API diretta.

## 🔑 Ottenere il Token BrightData

1. Vai su [BrightData Dashboard](https://brightdata.com/)
2. Accedi al tuo account
3. Naviga in **API Settings** o **Account Settings**
4. Copia il tuo **API Token**
5. Aggiungi il token in `backend/.env`:

```env
BRIGHTDATA_API_TOKEN=2a833260d04380b94fbde50dcb924b5f583c3b6138f138ef2bedf6e3396e2248
```

## 📋 Dataset IDs Configurati

Il sistema usa i seguenti dataset BrightData (già configurati nel codice):

- **Instagram**: `gd_l7q7dkf244hwjntr0`
- **Facebook**: `gd_lvhf8tq8ky28b3tbz`
- **Google Maps**: `gd_l7q7dkf244hwjku40`

> ⚠️ **Nota**: Se hai dataset IDs diversi, modificali in `backend/brightdata_integration.py`

## 🔄 Come Funziona

### 1. Sistema Asincrono

BrightData funziona in modo asincrono:
1. L'utente richiede dati social → viene creato un **job**
2. BrightData inizia il crawling in background
3. L'utente controlla lo stato del job periodicamente
4. Quando completato, l'utente recupera i risultati

### 2. Flusso Utente nel CMS

**Configurazione Iniziale:**
```
1. Utente inserisce gli URL completi nel CMS:
   - Instagram: https://www.instagram.com/username/
   - Facebook: https://www.facebook.com/pagename/
   - Google Maps: https://www.google.com/maps/place/...

2. Utente clicca "Aggiorna Dati Social"
```

**Processo di Aggiornamento:**
```
3. Sistema crea job BrightData per ogni piattaforma
4. Frontend mostra "Aggiornamento in corso..." con job_ids
5. Frontend fa polling ogni 30 secondi per controllare lo stato
6. Quando completato, mostra i nuovi dati aggiornati
```

## 🔌 API Endpoints

### Recupero Dati Social (Singolo)

```bash
# Instagram
GET /api/social/instagram-data?profile_url=https://www.instagram.com/username/
Response: {"job_id": "...", "status": "running", "message": "Crawl job started"}

# Facebook  
GET /api/social/facebook-likes?page_url=https://www.facebook.com/page/
Response: {"job_id": "...", "status": "running"}

# Google Maps
GET /api/social/google-reviews?place_url=https://www.google.com/maps/place/...
Response: {"job_id": "...", "status": "running"}
```

### Controllo Stato Job

```bash
GET /api/brightdata/job-status/{job_id}
Response: {
  "job_id": "...",
  "status": "ready",  # o "running", "failed"
  "progress": 100,
  "total_records": 1
}
```

### Recupero Risultati

```bash
GET /api/brightdata/job-results/{job_id}
Response: {
  "status": "success",
  "platform": "instagram",
  "data": {
    "followers": 15234,
    "posts": 542,
    "username": "username"
  }
}
```

### Aggiorna Tutti i Dati Social

```bash
POST /api/brightdata/refresh-all-social
Response: {
  "message": "Started 3 crawl jobs",
  "jobs": [
    {"platform": "instagram", "job_id": "..."},
    {"platform": "facebook", "job_id": "..."},
    {"platform": "googlemaps", "job_id": "..."}
  ]
}
```

### Lista Job Utente

```bash
GET /api/brightdata/my-jobs
Response: {
  "jobs": [
    {
      "job_id": "...",
      "platform": "instagram",
      "url": "...",
      "status": "completed",
      "results": {...},
      "created_at": "2025-10-06T..."
    }
  ]
}
```

## 📝 Formato Dati Restituiti

### Instagram

```json
{
  "followers": 15234,
  "posts": 542,
  "username": "username",
  "profile_url": "https://www.instagram.com/username/"
}
```

### Facebook

```json
{
  "fans": 8921,
  "reviews_count": 145,
  "rating": 4.5,
  "page_name": "Page Name"
}
```

### Google Maps

```json
{
  "reviews_count": 234,
  "rating": 4.3,
  "place_name": "Business Name",
  "address": "Via Roma 123, Milano"
}
```

## 🔧 Parametri Personalizzabili

### Facebook
```python
params = {
    "num_of_reviews": 50  # Numero di recensioni da raccogliere (default: 20)
}
```

### Google Maps
```python
params = {
    "days_limit": 30  # Giorni di recensioni da raccogliere (default: 30)
}
```

### Instagram
Nessun parametro specifico richiesto.

## ⏱️ Tempi di Crawling

- **Instagram**: ~30-60 secondi
- **Facebook**: ~60-90 secondi (con recensioni)
- **Google Maps**: ~45-75 secondi

I tempi possono variare in base al traffico di BrightData.

## 🛠️ Implementazione Frontend

### Esempio: Aggiornare Dati Instagram

```javascript
// 1. Avvia crawl
const startCrawl = async () => {
  const response = await fetch(
    `/api/social/instagram-data?profile_url=${encodeURIComponent(instagramUrl)}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  const data = await response.json();
  
  if (data.job_id) {
    // Salva job_id e inizia polling
    pollJobStatus(data.job_id, 'instagram');
  }
};

// 2. Polling dello stato
const pollJobStatus = async (jobId, platform) => {
  const checkStatus = async () => {
    const response = await fetch(`/api/brightdata/job-status/${jobId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const status = await response.json();
    
    if (status.status === 'ready') {
      // Job completato, recupera risultati
      fetchResults(jobId, platform);
    } else if (status.status === 'failed') {
      // Gestisci errore
      console.error('Job failed');
    } else {
      // Continua polling dopo 30 secondi
      setTimeout(checkStatus, 30000);
    }
  };
  
  checkStatus();
};

// 3. Recupera risultati
const fetchResults = async (jobId, platform) => {
  const response = await fetch(`/api/brightdata/job-results/${jobId}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const result = await response.json();
  
  // Aggiorna UI con i dati
  updateSocialData(platform, result.data);
};
```

## ⚠️ Gestione Errori

### Job Failed
```json
{
  "job_id": "...",
  "status": "failed",
  "error": "Invalid URL format"
}
```

### Job Timeout
Se un job non completa entro 5 minuti, viene considerato timeout. Puoi riprovare creando un nuovo job.

### Token Non Valido
```json
{
  "error": "BrightData API token not configured"
}
```

**Soluzione**: Verifica che `BRIGHTDATA_API_TOKEN` sia configurato in `backend/.env`

## 🔐 Sicurezza

- Il token BrightData è memorizzato solo sul backend
- Tutti gli endpoint richiedono autenticazione JWT
- Gli utenti possono vedere solo i propri job

## 📊 Database Collections

### brightdata_jobs
Memorizza tutti i job crawl:

```javascript
{
  user_id: "uuid",
  job_id: "snapshot_id",
  platform: "instagram",
  url: "https://...",
  status: "completed",
  results: {...},
  created_at: "2025-10-06T...",
  completed_at: "2025-10-06T..."
}
```

## 🆚 BrightData vs API Dirette

| Feature | BrightData | API Dirette |
|---------|-----------|-------------|
| Costo | Paghi per crawl | Gratuito (con limiti) |
| Autenticazione | Solo token API | Token + OAuth |
| Aggiornamento | Asincrono | Immediato |
| Rate Limits | Più flessibili | Restrittivi |
| Manutenzione | Gestita da BrightData | Aggiornamenti API |

## 🎯 Best Practices

1. **Cache i risultati**: Non fare crawl troppo frequenti (consigliato: 1x al giorno)
2. **Notifiche utente**: Informa l'utente che l'aggiornamento richiede tempo
3. **Gestione errori**: Prevedi fallback se BrightData non risponde
4. **Monitoraggio**: Traccia i job falliti per debugging

## 📞 Supporto

Per problemi con BrightData:
- [BrightData Support](https://brightdata.com/support)
- [BrightData Documentation](https://docs.brightdata.com/)

Per problemi con Look@Me CMS:
- Controlla i log backend: `tail -f /var/log/supervisor/backend.err.log`
- Verifica la collezione `brightdata_jobs` in MongoDB
