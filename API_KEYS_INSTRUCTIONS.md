# Look@Me CMS - API Keys Configuration Guide

Questo file contiene le istruzioni per ottenere e configurare tutte le API keys necessarie per il funzionamento completo del sistema Look@Me.

## File di Configurazione
Tutte le chiavi API vanno inserite nel file: `/app/backend/.env`

---

## 1. Google Maps API Key
**Variabile**: `GOOGLE_MAPS_API_KEY`

**Come ottenerla**:
1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Attiva l'API "Maps JavaScript API" e "Places API"
4. Vai su "Credenziali" → "Crea credenziali" → "Chiave API"
5. Copia la chiave e incollala nel file `.env`

**Documentazione**: https://developers.google.com/maps/documentation/javascript/get-api-key

---

## 2. TripAdvisor API Key
**Variabile**: `TRIPADVISOR_API_KEY`

**Come ottenerla**:
1. Registrati su [TripAdvisor Content API](https://www.tripadvisor.com/developers)
2. Crea una nuova applicazione
3. Copia l'API Key fornita
4. Incollala nel file `.env`

**Documentazione**: https://tripadvisor-content-api.readme.io/reference/overview

---

## 3. Facebook Access Token
**Variabile**: `FACEBOOK_ACCESS_TOKEN`

**Come ottenerlo**:
1. Vai su [Facebook Developers](https://developers.facebook.com/)
2. Crea una nuova app o seleziona una esistente
3. Aggiungi il prodotto "Facebook Login"
4. Vai su "Strumenti" → "Graph API Explorer"
5. Genera un Access Token con permessi: `pages_read_engagement`, `pages_show_list`
6. Per un token permanente, segui la guida: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived
7. Incollalo nel file `.env`

**Documentazione**: https://developers.facebook.com/docs/graph-api/

---

## 4. Instagram Access Token
**Variabile**: `INSTAGRAM_ACCESS_TOKEN`

**Come ottenerlo**:
1. L'account Instagram deve essere convertito in Business Account
2. Collegalo a una pagina Facebook
3. Segui la procedura su [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)
4. Oppure usa l'Instagram Graph API se hai un account Business: https://developers.facebook.com/docs/instagram-api/
5. Genera il token e incollalo nel file `.env`

**Documentazione**: https://developers.facebook.com/docs/instagram-api/getting-started

---

## 5. Gemini AI Key
**Variabile**: `GEMINI_API_KEY`

✅ **GIÀ CONFIGURATA** - La chiave è già presente nel file `.env`

Se necessiti di cambiarla:
1. Vai su [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clicca "Get API Key"
3. Copia la chiave e sostituiscila nel file `.env`

---

## Note Importanti

- ⚠️ **Sicurezza**: Non condividere mai le tue API keys pubblicamente
- 🔄 **Restart**: Dopo aver modificato il file `.env`, riavvia il backend con: `sudo supervisorctl restart backend`
- 💰 **Costi**: Alcune API potrebbero avere costi associati - verifica i piani pricing
- 📊 **Limiti**: Controlla i rate limits di ciascuna API per evitare blocchi

---

## Test delle Integrazioni

Dopo aver configurato le chiavi, puoi testare le integrazioni dal pannello CMS nella sezione "Test Connessioni".
