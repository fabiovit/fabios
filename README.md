# Fabio's 2.1.4

[![Release](https://img.shields.io/github/v/release/fabiovit/fabios?label=release)](https://github.com/fabiovit/fabios/releases)
![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5)
[![Validate](https://github.com/fabiovit/fabios/actions/workflows/validate.yml/badge.svg)](https://github.com/fabiovit/fabios/actions/workflows/validate.yml)
[![Hassfest](https://github.com/fabiovit/fabios/actions/workflows/hassfest.yml/badge.svg)](https://github.com/fabiovit/fabios/actions/workflows/hassfest.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


**Shared expenses, made simple. / Spese condivise, senza complicazioni.**

Fabio's is a Home Assistant custom integration for managing shared expenses directly inside Home Assistant.  
Fabio's è un'integrazione custom per Home Assistant pensata per gestire le spese condivise direttamente da Home Assistant.

[Italiano](#italiano) · [English](#english)

---

## Italiano

### Funzioni principali

- Dashboard completa **Fabio's** nella sidebar di Home Assistant
- **Fabio's Lite**, interfaccia semplificata e ottimizzata per smartphone
- modifica ed eliminazione delle spese direttamente da **Fabio's Lite**
- WebApp standalone installabile dalla schermata Home dello smartphone
- modifica ed eliminazione delle spese anche nella **WebApp standalone**
- versione della WebApp sincronizzata automaticamente con la versione installata di Fabio's
- persone e gruppi multipli
- spese condivise con quote personalizzabili
- saldi automatici, registrazione dei rimborsi e chiusura del mese
- possibilità di **saldare il mese** oppure **riportare il saldo al mese successivo** senza modificare le spese originali
- spese ricorrenti non retroattive
- gestione delle rate con stato visibile, ad esempio **Rata 9/12**
- modifica ed eliminazione delle spese
- categorie e statistiche mensili
- importazione PDF, XLSX e CSV con anteprima
- backup/import JSON
- **export CSV del mese selezionato**
- divisioni 50/50 mostrate correttamente anche quando l'importo richiede un arrotondamento di 1 centesimo
- sensori Home Assistant
- storage locale persistente
- interfaccia responsive
- traduzioni Home Assistant in italiano e inglese

### Installazione con HACS

1. Apri HACS.
2. Aggiungi `https://github.com/fabiovit/fabios` come repository personalizzato di tipo **Integration**.
3. Installa **Fabio's**.
4. Riavvia Home Assistant.
5. Vai in **Impostazioni → Dispositivi e servizi → Aggiungi integrazione** e cerca **Fabio's**.

### Installazione manuale

Copia:

`custom_components/fabios`

in:

`/config/custom_components/fabios`

Riavvia Home Assistant e aggiungi l'integrazione da **Impostazioni → Dispositivi e servizi**.

### Fabio's Lite

Dopo l'installazione è disponibile il pannello:

`/fabios-lite`

Utilizza gli stessi dati della dashboard completa ma con un'interfaccia più semplice. Le spese già inserite possono essere modificate o eliminate direttamente dalla sezione **Spese**.

### WebApp standalone

Fabio's espone anche:

`/fabios-app/`

Aprila in Safari su iPhone/iPad e usa **Condividi → Aggiungi alla schermata Home** per creare un'icona dedicata a Fabio's.

La WebApp utilizza l'autenticazione Home Assistant: non crea un secondo archivio e non richiede credenziali separate. Dalla versione 2.1.4 mostra automaticamente la versione realmente installata di Fabio's e forza l'aggiornamento della shell su iOS dopo gli upgrade.

### Rate e ricorrenti

Le spese rateali mostrano il progresso direttamente nelle interfacce Lite e WebApp, ad esempio:

`Rata 9/12`

Le spese ricorrenti rispettano sempre la loro data di inizio e **non vengono generate retroattivamente**.

### Dati e privacy

I dati di Fabio's vengono salvati localmente nello storage di Home Assistant.  
La pagina pubblica della WebApp non espone dati: l'accesso alle informazioni avviene tramite l'autenticazione di Home Assistant.

### Licenza

MIT License © 2026 Fabio Vittori.

---

## English

### Main features

- Full **Fabio's** dashboard in the Home Assistant sidebar
- **Fabio's Lite**, a simplified mobile-first interface
- edit and delete expenses directly from **Fabio's Lite**
- Standalone WebApp that can be added to a smartphone Home Screen
- edit and delete expenses in the **standalone WebApp** as well
- WebApp version automatically synchronized with the installed Fabio's version
- multiple people and groups
- shared expenses with customizable shares
- automatic balances, settlement tracking and month closing
- option to **settle a month** or **carry its balance into the next month** without changing the original expenses
- non-retroactive recurring expenses
- installment tracking with visible progress, e.g. **Installment 9/12**
- expense editing and deletion
- categories and monthly statistics
- PDF, XLSX and CSV import with preview
- JSON backup/import
- **CSV export for the selected month**
- 50/50 splits remain displayed as 50/50 when a one-cent rounding difference is required
- Home Assistant sensors
- persistent local storage
- responsive interface
- Home Assistant translations in Italian and English

### Install with HACS

1. Open HACS.
2. Add `https://github.com/fabiovit/fabios` as a custom **Integration** repository.
3. Install **Fabio's**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and search for **Fabio's**.

### Manual installation

Copy:

`custom_components/fabios`

to:

`/config/custom_components/fabios`

Restart Home Assistant and add the integration from **Settings → Devices & services**.

### Fabio's Lite

After installation, the simplified panel is available at:

`/fabios-lite`

It uses the same data as the full dashboard. Existing expenses can be edited or deleted directly from the **Expenses** section.

### Standalone WebApp

Fabio's also provides:

`/fabios-app/`

Open it in Safari on iPhone/iPad and use **Share → Add to Home Screen** to create a dedicated Fabio's icon.

The WebApp uses Home Assistant authentication and does not create a separate database or require separate credentials. Starting with 2.1.4, it displays the actually installed Fabio's version automatically and forces the app shell to refresh on iOS after upgrades.

### Installments and recurring expenses

Installment expenses show their progress directly in Lite and the standalone WebApp, for example:

`Installment 9/12`

Recurring expenses always respect their configured start date and are **never generated retroactively**.

### Data and privacy

Fabio's data is stored locally in Home Assistant storage.  
The public WebApp shell exposes no expense data; access to data is protected by Home Assistant authentication.

### License

MIT License © 2026 Fabio Vittori.
