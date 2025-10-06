# 🚀 Setup Locale Look@Me CMS - Guida Rapida

## ✅ File Pronti per GitHub

Tutti i file necessari sono stati preparati e committati:

- ✅ `frontend/yarn.lock` - File di lock delle dipendenze Node
- ✅ `backend/.env.example` - Template configurazione backend
- ✅ `frontend/.env.example` - Template configurazione frontend
- ✅ `docker-compose.yml` - Configurato per usare file .env
- ✅ `README.md` - Documentazione completa aggiornata

## 📤 Prossimi Passaggi

### 1. Salva su GitHub da Emergent

Nell'interfaccia di Emergent:
1. Clicca il pulsante **"Save to GitHub"** nella chat
2. Seleziona il branch (o crea nuovo branch: `feature/yarn-lock-fix`)
3. Clicca **"PUSH TO GITHUB"**

### 2. Sul Tuo Computer Locale

```bash
# Naviga nella cartella del progetto
cd path/to/look-at-me-cms

# Scarica le modifiche
git pull origin main
# oppure se hai creato un nuovo branch:
git pull origin feature/yarn-lock-fix

# Verifica che yarn.lock sia presente
ls -l frontend/yarn.lock
```

### 3. Configura le Variabili d'Ambiente

```bash
# Copia i template
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**Modifica `backend/.env`:**
```env
MONGO_URL=mongodb://mongodb:27017/lookatme_cms
JWT_SECRET=tua_chiave_segreta_molto_lunga_e_casuale
EMERGENT_LLM_KEY=sk-emergent-xxxxxxxxxxxxxxxx

# BrightData Integration (OBBLIGATORIO per social media)
BRIGHTDATA_API_TOKEN=your_brightdata_token_here

# TripAdvisor (Opzionale)
TRIPADVISOR_API_KEY=

# Le API dirette di Google/Facebook/Instagram non sono più necessarie
```

> 📚 Per maggiori dettagli su BrightData, vedi [BRIGHTDATA_SETUP.md](./BRIGHTDATA_SETUP.md)

**Il file `frontend/.env` è già OK:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 4. Avvia con Docker

```bash
# Avvia tutti i servizi
docker-compose up --build

# Oppure in background
docker-compose up -d --build
```

Attendi che tutti i servizi siano pronti (~2-3 minuti alla prima esecuzione).

### 5. Accedi all'Applicazione

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 🔑 Ottenere l'Emergent LLM Key

Se non hai ancora la chiave Emergent:

1. Accedi al tuo account Emergent
2. Clicca sull'icona del profilo (in alto)
3. Vai su **"Universal Key"**
4. Copia la chiave
5. Incollala in `backend/.env` come valore di `EMERGENT_LLM_KEY`

## ✅ Verifica che Funzioni

Dopo aver avviato Docker:

```bash
# Test backend
curl http://localhost:8001/api/health

# Risposta attesa:
# {"status":"healthy","timestamp":"..."}

# Test frontend
curl http://localhost:3000

# Dovrebbe restituire HTML della pagina
```

## 🐛 Problemi Comuni

### Errore: "yarn.lock not found"
**Soluzione**: Assicurati di aver fatto il `git pull` dopo aver salvato su GitHub da Emergent.

### Errore: "Port already in use"
**Soluzione**: 
```bash
# Ferma i container
docker-compose down

# Oppure cambia le porte in docker-compose.yml
```

### Errore: "EMERGENT_LLM_KEY not configured"
**Soluzione**: Aggiungi la tua chiave Emergent in `backend/.env` come spiegato sopra.

### MongoDB non si avvia
**Soluzione**:
```bash
# Rimuovi il volume e ricrea
docker-compose down -v
docker-compose up --build
```

## 📊 Comandi Docker Utili

```bash
# Vedi lo stato dei container
docker-compose ps

# Vedi i log
docker-compose logs -f

# Vedi i log di un servizio specifico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb

# Ferma tutto
docker-compose down

# Ferma e rimuovi volumi (reset completo)
docker-compose down -v

# Ricostruisci senza cache
docker-compose build --no-cache
```

## 🎉 Completato!

Una volta che Docker è avviato e funzionante, puoi:
- Registrare un nuovo utente su http://localhost:3000
- Configurare il tuo store dal dashboard CMS
- Testare le integrazioni social (se hai le chiavi API)
- Calcolare il punteggio di sostenibilità con Gemini AI

Buon sviluppo! 🚀
