# Changelog

## 2.1.5 — 2026-09-02

### Italiano
- La visualizzazione delle spese mostra ora la **divisione percentuale** in tutte le interfacce: dashboard completa Fabio's, Fabio's Lite e WebApp standalone.
- Ogni spesa indica chiaramente come è ripartito l'importo, ad esempio `Fabio Vittori 50% · Fabio Saleri 50%` oppure `Fabio Vittori 0% · Fabio Saleri 100%`.
- Le vere divisioni 50/50 restano mostrate come `50% / 50%` anche quando l'importo richiede un arrotondamento di un centesimo.
- Allineati i badge versione della dashboard completa e di Fabio's Lite alla release corrente.
- Corretta anche la visualizzazione 50/50 nella modifica delle spese ricorrenti.
- Corretta una piccola imprecisione nell'escaping HTML del frontend completo.

### English
- Expense rows now show the **percentage split** across all interfaces: the full Fabio's dashboard, Fabio's Lite and the standalone WebApp.
- Each expense clearly shows how the amount is split, for example `Fabio Vittori 50% · Fabio Saleri 50%` or `Fabio Vittori 0% · Fabio Saleri 100%`.
- True 50/50 splits remain displayed as `50% / 50%` even when the amount requires a one-cent rounding difference.
- Version badges in the full dashboard and Fabio's Lite have been aligned with the current release.
- Fixed 50/50 display when editing recurring expenses.
- Fixed a small HTML escaping issue in the full frontend.

## 2.1.4 — 2026-09-02

### Italiano
- La WebApp standalone mostra ora automaticamente la versione realmente installata di Fabio's invece di usare un numero di versione scritto a mano.
- Migliorato il refresh della WebApp su iPhone/iPad dopo gli aggiornamenti, con shell e service worker senza cache persistente.
- Aggiunta nella **WebApp standalone** la possibilità di modificare ed eliminare le spese già inserite, in linea con Fabio's Lite.
- Durante la modifica vengono mantenuti pagatore, data, categoria, note, divisione originale ed eventuali informazioni di rata.
- Le divisioni personalizzate vengono conservate anche se cambia l'importo.

### English
- The standalone WebApp now displays the actually installed Fabio's version instead of using a hard-coded version number.
- Improved WebApp refresh behavior on iPhone/iPad after upgrades, with a non-persistent app shell and service-worker cache.
- Added the ability to edit and delete existing expenses directly in the **standalone WebApp**, matching Fabio's Lite.
- Editing preserves payer, date, category, notes, the original split and installment metadata when present.
- Custom splits are preserved even when the amount is changed.

## 2.1.3 — 2026-09-01

### Italiano
- Aggiunta in **Fabio's Lite** la possibilità di modificare ed eliminare le spese già inserite direttamente dalla sezione Spese.
- Durante la modifica in Lite vengono mantenuti pagatore, data, categoria, note e divisione originale.
- Le divisioni personalizzate vengono conservate anche se si modifica l'importo.

### English
- Added the ability to edit and delete existing expenses directly from the Expenses section in **Fabio's Lite**.
- Lite editing preserves payer, date, category, notes and the original split.
- Custom splits are preserved even when the amount is changed.

## 2.1.2 — 2026-09-01

### Italiano
- Corretto il modo in cui le divisioni 50/50 vengono mostrate nella schermata di modifica.
- Per importi non divisibili esattamente al centesimo, ad esempio 19,99 €, Fabio's continua a salvare correttamente quote come 9,99 € + 10,00 €, ma ora mostra di nuovo 50,00% / 50,00% invece delle percentuali ricostruite 49,97% / 50,03%.
- Nessuna modifica alla logica dei saldi o alle quote monetarie salvate.

### English
- Fixed how 50/50 splits are displayed in the expense edit screen.
- For amounts that cannot be divided evenly to the cent, such as €19.99, Fabio's still stores the correct €9.99 + €10.00 shares while showing 50.00% / 50.00% instead of reconstructed 49.97% / 50.03% percentages.
- No changes to balance calculations or stored monetary shares.

## 2.1.1 — 2026-09-01

### Italiano
- Corretto il download del backup JSON.
- Aggiunto l'export CSV del mese selezionato nella sezione Spese.
- Il CSV include data, descrizione, categoria, importo, pagatore, quote per persona, rate e note.
- Migliorato il cache-busting del frontend dopo gli aggiornamenti.

### English
- Fixed JSON backup downloads.
- Added CSV export for the selected month in the Expenses section.
- CSV exports include date, description, category, amount, payer, per-person shares, installments and notes.
- Improved frontend cache-busting after upgrades.

## 2.1.0 — 2026-08-29

### Italiano
- Aggiunta la chiusura del mese nella sezione Saldi.
- È ora possibile saldare automaticamente il saldo mensile registrando i rimborsi necessari.
- È ora possibile riportare il saldo residuo al mese successivo senza modificare le spese originali.
- I riporti sono registrati separatamente e non alterano statistiche o totali delle spese.
- Funzione disponibile nella dashboard completa, Fabio's Lite e WebApp standalone.

### English
- Added month closing to the Balances section.
- Monthly balances can now be settled automatically by recording the required settlements.
- Outstanding balances can be carried into the next month without changing original expenses.
- Carry-overs are stored separately and do not affect expense statistics or totals.
- Available in the full dashboard, Fabio's Lite and the standalone WebApp.

## 2.0.0 — 2026-08-29

### Italiano
- Prima release pubblica stabile di Fabio's.
- Aggiunta WebApp standalone per smartphone.
- Fabio's Lite ottimizzato per l'uso mobile.
- Visualizzazione dello stato delle rate in Lite e WebApp (`Rata 9/12`).
- Gestione completa di spese, saldi, rimborsi, ricorrenti e rate.
- Ricorrenti non retroattive.
- Import PDF/XLSX/CSV e backup JSON.
- Aggiunti asset brand locali, HACS Action e Hassfest con badge di stato nel README.
- Documentazione e traduzioni italiano/inglese.
- Migliorata la robustezza del caricamento frontend durante i reload della config entry.
- Manifest ordinato secondo Hassfest e rimossa la configurazione YAML non utilizzata.

### English
- First stable public release of Fabio's.
- Added a standalone smartphone WebApp.
- Improved Fabio's Lite for mobile use.
- Installment progress is now visible in Lite and WebApp (`Installment 9/12`).
- Complete management of expenses, balances, settlements, recurring expenses and installments.
- Recurring expenses are non-retroactive.
- PDF/XLSX/CSV import and JSON backup.
- Added local brand assets, HACS Action and Hassfest with status badges in the README.
- Italian/English documentation and translations.
- Improved frontend registration robustness during config-entry reloads.
- Fixed manifest ordering for Hassfest and removed unused YAML setup.
