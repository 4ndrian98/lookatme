# 🪟 Look@Me CMS - Guida Setup Windows

Guida passo-passo per avviare Look@Me CMS su Windows con Docker Desktop.

## ✅ Prerequisiti

### 1. Installa Docker Desktop per Windows

**Se NON hai Docker Desktop installato:**

1. Scarica Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Esegui l'installer
3. Durante l'installazione:
   - ✅ Abilita "Use WSL 2 instead of Hyper-V" (consigliato)
   - ✅ Accetta tutte le impostazioni predefinite
4. Riavvia il computer quando richiesto
5. Avvia Docker Desktop dal menu Start

### 2. Verifica Installazione

Apri **PowerShell** e digita:

```powershell
docker --version
docker-compose --version
```

Dovresti vedere qualcosa tipo:
```
Docker version 24.0.x, build xxxxx
Docker Compose version v2.x.x
```

✅ Se vedi le versioni, sei pronto!
❌ Se vedi errori, Docker Desktop non è installato correttamente.

---

## 🚀 Avvio Look@Me CMS

### Passo 1: Assicurati che Docker Desktop sia in esecuzione

1. Cerca "Docker Desktop" nel menu Start
2. Apri l'applicazione
3. **IMPORTANTE**: Aspetta che l'icona della balena in basso a destra smetta di animarsi
4. L'icona diventerà statica quando Docker è pronto

![Docker Desktop Ready](https://via.placeholder.com/300x100/4CAF50/FFFFFF?text=Docker+Ready)

### Passo 2: Apri PowerShell nella cartella del progetto

```powershell
cd "C:\Users\ITS\Desktop\CORSO AI Andrian Ghiba\lookatme"
```

### Passo 3: Avvia i container

```powershell
docker-compose up --build
```

**Cosa succede:**
- Scarica le immagini Docker (prima volta, richiede qualche minuto)
- Costruisce backend e frontend
- Avvia MongoDB, Backend, Frontend

**Quando vedi:**
```
lookatme-backend-1   | INFO:     Application startup complete.
lookatme-frontend-1  | ...
lookatme-mongodb-1   | ...
```

✅ **L'applicazione è pronta!**

### Passo 4: Accedi all'applicazione

Apri il browser e vai a:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/docs

---

## 🛑 Come Fermare l'Applicazione

### Opzione 1: Ferma con Ctrl+C
Se hai avviato con `docker-compose up` (senza `-d`):
1. Premi `Ctrl + C` nella finestra PowerShell
2. Aspetta che i container si fermino

### Opzione 2: Ferma in background
Se hai avviato con `docker-compose up -d`:

```powershell
docker-compose down
```

---

## 🔧 Comandi Utili per Windows

### Visualizza container in esecuzione
```powershell
docker ps
```

### Visualizza logs
```powershell
# Tutti i servizi
docker-compose logs

# Solo backend
docker-compose logs backend

# Solo frontend  
docker-compose logs frontend

# Segui i logs in tempo reale
docker-compose logs -f
```

### Riavvia un servizio specifico
```powershell
docker-compose restart backend
docker-compose restart frontend
docker-compose restart mongodb
```

### Ricostruisci le immagini
```powershell
docker-compose build --no-cache
docker-compose up -d
```

### Pulisci tutto e ricomincia
```powershell
# Ferma e rimuovi container
docker-compose down

# Ferma e rimuovi anche i volumi (⚠️ CANCELLA I DATI!)
docker-compose down -v

# Riavvia da zero
docker-compose up --build
```

---

## ❌ Risoluzione Problemi Comuni

### Errore: "The system cannot find the file specified"

**Causa**: Docker Desktop non è in esecuzione

**Soluzione**:
1. Apri Docker Desktop dal menu Start
2. Aspetta che sia completamente avviato (icona balena ferma)
3. Riprova il comando

---

### Errore: "Port already in use"

**Causa**: Le porte 3000, 8001 o 27017 sono già occupate

**Soluzione**:

#### Trova cosa sta usando la porta:
```powershell
# Controlla porta 3000 (frontend)
netstat -ano | findstr :3000

# Controlla porta 8001 (backend)
netstat -ano | findstr :8001

# Controlla porta 27017 (mongodb)
netstat -ano | findstr :27017
```

#### Termina il processo:
```powershell
# Sostituisci 1234 con il PID trovato
taskkill /PID 1234 /F
```

**Oppure** modifica le porte nel `docker-compose.yml`:
```yaml
services:
  frontend:
    ports:
      - "3001:80"  # Cambia 3000 in 3001
  backend:
    ports:
      - "8002:8001"  # Cambia 8001 in 8002
```

---

### Errore: "Insufficient resources"

**Causa**: Docker Desktop ha poca memoria allocata

**Soluzione**:
1. Apri Docker Desktop
2. Vai su Settings (icona ingranaggio)
3. Resources → Advanced
4. Aumenta Memory a almeno 4GB
5. Clicca "Apply & Restart"

---

### Errore: "WSL 2 installation is incomplete"

**Causa**: WSL 2 non è configurato correttamente

**Soluzione**:
1. Apri PowerShell come Amministratore
2. Esegui:
```powershell
wsl --install
wsl --set-default-version 2
```
3. Riavvia il computer
4. Riapri Docker Desktop

---

### Il frontend mostra errore di connessione al backend

**Soluzione**:

1. Verifica che il backend sia attivo:
```powershell
curl http://localhost:8001/api/health
```

2. Se non risponde, controlla i logs:
```powershell
docker-compose logs backend
```

3. Se vedi errori Python, ricostruisci:
```powershell
docker-compose down
docker-compose up --build
```

---

## 📁 Struttura Directory Windows

Assicurati che la tua cartella abbia questa struttura:

```
C:\Users\ITS\Desktop\CORSO AI Andrian Ghiba\lookatme\
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.conf
```

---

## 🌐 Configurazione API Keys (Opzionale)

Se vuoi abilitare le integrazioni social media:

### 1. Crea il file `.env` nella root:

```powershell
Copy-Item .env.docker .env
```

### 2. Apri `.env` con Notepad:

```powershell
notepad .env
```

### 3. Inserisci le tue chiavi:

```env
GOOGLE_MAPS_API_KEY=la_tua_chiave
TRIPADVISOR_API_KEY=la_tua_chiave
FACEBOOK_ACCESS_TOKEN=il_tuo_token
INSTAGRAM_ACCESS_TOKEN=il_tuo_token
```

### 4. Salva e riavvia:

```powershell
docker-compose restart backend
```

📖 Vedi `API_KEYS_INSTRUCTIONS.md` per ottenere le chiavi.

---

## 💡 Tips per Windows

### Usa Windows Terminal
Windows Terminal è più potente di PowerShell standard:
- Scarica dal Microsoft Store
- Supporta tab multipli
- Migliore visualizzazione colori

### Path con spazi
Se il percorso contiene spazi, usa le virgolette:
```powershell
cd "C:\Users\ITS\Desktop\CORSO AI Andrian Ghiba\lookatme"
```

### Permessi Amministratore
Alcuni comandi potrebbero richiedere PowerShell come Amministratore:
- Tasto destro su PowerShell → "Esegui come amministratore"

---

## ✅ Checklist Finale

Prima di avviare, verifica:

- [ ] Docker Desktop installato
- [ ] Docker Desktop in esecuzione (icona balena attiva)
- [ ] PowerShell aperto nella cartella progetto
- [ ] Nessun altro servizio usa porte 3000, 8001, 27017
- [ ] Almeno 4GB RAM disponibili

Poi esegui:
```powershell
docker-compose up --build
```

---

## 🎉 Successo!

Quando vedi questo output:
```
lookatme-backend-1   | INFO:     Uvicorn running on http://0.0.0.0:8001
lookatme-frontend-1  | Starting nginx...
lookatme-mongodb-1   | MongoDB ready
```

✅ Vai su http://localhost:3000 e inizia a usare Look@Me CMS!

---

## 📞 Serve Aiuto?

1. Controlla i logs: `docker-compose logs -f`
2. Verifica Docker Desktop sia attivo
3. Consulta `DOCKER_DEPLOY.md` per troubleshooting avanzato

**Buon lavoro! 🚀**
