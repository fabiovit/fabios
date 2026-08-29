
class FabiosLitePanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._started) {
      this._started = true;
      this.attachShadow({mode:"open"});
      this.month = new Date().toISOString().slice(0,7);
      this.gid = null;
      this.tab = "home";
      this.load();
    }
  }

  async ws(type, payload={}) {
    return await this._hass.connection.sendMessagePromise({type, ...payload});
  }

  esc(v) {
    return String(v ?? "").replace(/[&<>"']/g, c => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    }[c]));
  }

  money(v) {
    return new Intl.NumberFormat("it-IT", {
      style:"currency",
      currency:this.state?.settings?.currency || "EUR"
    }).format(Number(v || 0));
  }

  person(id) {
    return this.state?.people?.find(p=>p.id===id)?.name || "—";
  }

  group() {
    return this.state?.groups?.find(g=>g.id===this.gid);
  }

  members() {
    const g=this.group();
    return (g?.members || []).map(id=>this.state.people.find(p=>p.id===id)).filter(Boolean);
  }

  monthLabel() {
    const [y,m]=this.month.split("-").map(Number);
    return new Intl.DateTimeFormat("it-IT",{month:"long",year:"numeric"})
      .format(new Date(y,m-1,1));
  }

  async load() {
    try {
      const payload={month:this.month};
      if(this.gid) payload.group_id=this.gid;
      this.state=await this.ws("fabios/get_state",payload);
      this.gid=this.state.active_group_id;
      this.month=this.state.selected_month || this.month;
      this.render();
    } catch(e) {
      this.shadowRoot.innerHTML=`
        <style>:host{display:block;padding:24px;font-family:system-ui;color:var(--primary-text-color)}</style>
        <div>Errore Fabio’s Lite: ${this.esc(e.message||e)}</div>`;
    }
  }

  shiftMonth(delta) {
    const [y,m]=this.month.split("-").map(Number);
    const d=new Date(y,m-1+delta,1);
    this.month=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
    this.load();
  }

  expenses() {
    return [...(this.state?.expenses||[])]
      .filter(e=>e.group_id===this.gid && String(e.date||"").startsWith(this.month))
      .sort((a,b)=>String(b.date||"").localeCompare(String(a.date||"")));
  }

  currentBalance() {
    return (this.state?.balances||[])[0] || null;
  }

  render() {
    const expenses=this.expenses();
    const balance=this.currentBalance();
    const total=this.state?.summary?.month_total || 0;
    const members=this.members();

    this.shadowRoot.innerHTML=`
      <style>
        :host{display:block;min-height:100%;background:var(--primary-background-color);color:var(--primary-text-color);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
        *{box-sizing:border-box}
        .app{max-width:680px;margin:0 auto;padding:18px 16px 88px}
        .top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px}
        .brand{font-size:26px;font-weight:800;letter-spacing:-.7px}
        .sub{font-size:12px;color:var(--secondary-text-color)}
        .month{display:flex;align-items:center;justify-content:center;gap:10px;margin:12px 0 18px}
        button{border:0;border-radius:14px;padding:12px 15px;background:var(--secondary-background-color);color:inherit;font:inherit;font-weight:700;min-height:44px;cursor:pointer}
        button.primary{background:var(--primary-color);color:white}
        button.ghost{background:transparent;border:1px solid var(--divider-color)}
        .hero{padding:22px;border:1px solid var(--divider-color);border-radius:24px;background:var(--card-background-color);margin-bottom:14px}
        .eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--secondary-text-color)}
        .big{font-size:38px;font-weight:850;letter-spacing:-1.4px;margin:7px 0 4px}
        .balance{font-size:18px;font-weight:750}
        .actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}
        .section{margin-top:22px}
        .section h3{margin:0 0 10px;font-size:17px}
        .row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 0;border-bottom:1px solid var(--divider-color)}
        .desc{font-weight:720}.meta{font-size:12px;color:var(--secondary-text-color);margin-top:3px}.amount{font-weight:800;white-space:nowrap}.ratebadge{display:inline-flex;align-items:center;margin-top:6px;padding:4px 8px;border:1px solid var(--divider-color);border-radius:999px;font-size:11px;font-weight:800;color:var(--primary-color);background:var(--secondary-background-color)}
        .nav{position:sticky;bottom:10px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;background:var(--card-background-color);padding:8px;border:1px solid var(--divider-color);border-radius:20px;margin-top:24px}
        .nav button{padding:10px 6px;background:transparent;font-size:12px}
        .nav button.active{background:var(--secondary-background-color)}
        dialog{border:1px solid var(--divider-color);border-radius:22px;background:var(--card-background-color);color:inherit;width:min(92vw,560px);padding:0}
        dialog::backdrop{background:rgba(0,0,0,.65)}
        .modal{padding:20px}
        label{display:block;font-size:12px;color:var(--secondary-text-color);margin:12px 0 6px}
        input,select{width:100%;border:1px solid var(--divider-color);border-radius:12px;background:var(--secondary-background-color);color:inherit;padding:12px;font-size:16px;min-height:44px}
        .splitpreset{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:8px}
        .modalactions{display:flex;justify-content:flex-end;gap:8px;margin-top:18px}
        .empty{padding:20px 0;color:var(--secondary-text-color);text-align:center}
        @media(max-width:420px){.big{font-size:32px}.actions{grid-template-columns:1fr}.app{padding-left:12px;padding-right:12px}}
      </style>

      <div class="app">
        <div class="top">
          <div>
            <div class="brand">Fabio’s</div>
            <div class="sub">Lite · spese condivise · v2.0.0</div>
          </div>
          <button class="ghost" id="refresh">↻</button>
        </div>

        ${this.tab==="home" ? this.homeView(balance,total,expenses) : ""}
        ${this.tab==="expenses" ? this.expensesView(expenses) : ""}
        ${this.tab==="balance" ? this.balanceView(balance) : ""}

        <div class="nav">
          <button data-tab="home" class="${this.tab==="home"?"active":""}">Home</button>
          <button data-tab="expenses" class="${this.tab==="expenses"?"active":""}">Spese</button>
          <button data-tab="balance" class="${this.tab==="balance"?"active":""}">Saldo</button>
        </div>
      </div>

      ${this.expenseDialog(members)}
      ${this.settlementDialog(members)}
    `;
    this.bind();
  }

  monthNav(){
    return `<div class="month">
      <button class="ghost" id="prevMonth">‹</button>
      <strong style="text-transform:capitalize">${this.monthLabel()}</strong>
      <button class="ghost" id="nextMonth">›</button>
    </div>`;
  }

  homeView(balance,total,expenses){
    const txt=balance
      ? `${this.person(balance.from_person)} deve ${this.money(balance.amount)} a ${this.person(balance.to_person)}`
      : `Tutto regolato per questo mese`;
    return `
      ${this.monthNav()}
      <div class="hero">
        <div class="eyebrow">Spese del mese</div>
        <div class="big">${this.money(total)}</div>
        <div class="balance">${this.esc(txt)}</div>
      </div>
      <div class="actions">
        <button class="primary" id="newExpense">＋ Nuova spesa</button>
        <button id="settle">${balance?"Registra rimborso":"Saldo regolato"}</button>
      </div>
      <div class="section">
        <h3>Ultime spese</h3>
        ${expenses.length ? expenses.slice(0,6).map(e=>this.expenseRow(e)).join("") : `<div class="empty">Nessuna spesa.</div>`}
      </div>`;
  }

  expensesView(expenses){
    return `
      ${this.monthNav()}
      <div class="section">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
          <h3 style="margin:0">Spese</h3>
          <button class="primary" id="newExpense">＋ Aggiungi</button>
        </div>
        ${expenses.length ? expenses.map(e=>this.expenseRow(e)).join("") : `<div class="empty">Nessuna spesa.</div>`}
      </div>`;
  }

  balanceView(balance){
    return `
      ${this.monthNav()}
      <div class="hero">
        <div class="eyebrow">Saldo del mese</div>
        ${balance
          ? `<div class="big">${this.money(balance.amount)}</div><div class="balance">${this.esc(this.person(balance.from_person))} deve pagare ${this.esc(this.person(balance.to_person))}</div>`
          : `<div class="big">0,00 €</div><div class="balance">Tutto regolato</div>`}
      </div>
      ${balance ? `<button class="primary" id="settle" style="width:100%">Registra rimborso</button>` : ""}`;
  }

  expenseRow(e){
    const installment=(e.installment_current&&e.installment_total)
      ? `<div class="ratebadge">Rata ${this.esc(e.installment_current)}/${this.esc(e.installment_total)}</div>`
      : "";
    return `<div class="row">
      <div style="min-width:0">
        <div class="desc">${this.esc(e.description)}</div>
        ${installment}
        <div class="meta">${this.esc(this.person(e.paid_by))} ha pagato · ${this.esc(e.date)}</div>
      </div>
      <div class="amount">${this.money(e.amount)}</div>
    </div>`;
  }

  expenseDialog(members){
    const opts=members.map(p=>`<option value="${p.id}">${this.esc(p.name)}</option>`).join("");
    return `<dialog id="expDlg"><div class="modal">
      <h2 style="margin-top:0">Nuova spesa</h2>
      <label>Descrizione</label><input id="d" placeholder="Es. Spesa, cena, benzina">
      <label>Importo</label><input id="a" type="number" min="0.01" step="0.01" inputmode="decimal">
      <label>Pagato da</label><select id="payer">${opts}</select>
      <label>Data</label><input id="dt" type="date" value="${new Date().toISOString().slice(0,10)}">
      <label>Divisione</label>
      <div class="splitpreset">
        <button type="button" data-split="equal">50 / 50</button>
        <button type="button" data-split="payer">Tutto chi paga</button>
        ${members[0]?`<button type="button" data-split="${members[0].id}">100% ${this.esc(members[0].name)}</button>`:""}
        ${members[1]?`<button type="button" data-split="${members[1].id}">100% ${this.esc(members[1].name)}</button>`:""}
      </div>
      <div id="splitInfo" class="meta" style="margin-top:10px">Divisione 50 / 50</div>
      <div class="modalactions">
        <button class="ghost close">Annulla</button>
        <button class="primary" id="save">Salva</button>
      </div>
    </div></dialog>`;
  }

  settlementDialog(members){
    const opts=members.map(p=>`<option value="${p.id}">${this.esc(p.name)}</option>`).join("");
    return `<dialog id="setDlg"><div class="modal">
      <h2 style="margin-top:0">Registra rimborso</h2>
      <label>Da</label><select id="sf">${opts}</select>
      <label>A</label><select id="st">${opts}</select>
      <label>Importo</label><input id="sa" type="number" min="0.01" step="0.01">
      <label>Data</label><input id="sd" type="date" value="${new Date().toISOString().slice(0,10)}">
      <div class="modalactions">
        <button class="ghost close">Annulla</button>
        <button class="primary" id="saveSet">Salva</button>
      </div>
    </div></dialog>`;
  }

  bind(){
    const q=s=>this.shadowRoot.querySelector(s);
    const qa=s=>[...this.shadowRoot.querySelectorAll(s)];

    q("#refresh")?.addEventListener("click",()=>this.load());
    q("#prevMonth")?.addEventListener("click",()=>this.shiftMonth(-1));
    q("#nextMonth")?.addEventListener("click",()=>this.shiftMonth(1));
    qa("[data-tab]").forEach(b=>b.addEventListener("click",()=>{this.tab=b.dataset.tab;this.render()}));
    q("#newExpense")?.addEventListener("click",()=>this.openExpense());
    q("#settle")?.addEventListener("click",()=>this.openSettlement());
    qa(".close").forEach(b=>b.addEventListener("click",()=>b.closest("dialog").close()));
    qa("[data-split]").forEach(b=>b.addEventListener("click",()=>this.chooseSplit(b.dataset.split)));
    q("#save")?.addEventListener("click",()=>this.saveExpense());
    q("#saveSet")?.addEventListener("click",()=>this.saveSettlement());
  }

  openExpense(){
    this.splitMode="equal";
    const q=s=>this.shadowRoot.querySelector(s);
    q("#d").value="";
    q("#a").value="";
    q("#dt").value=new Date().toISOString().slice(0,10);
    q("#splitInfo").textContent="Divisione 50 / 50";
    q("#expDlg").showModal();
  }

  chooseSplit(mode){
    this.splitMode=mode;
    const q=s=>this.shadowRoot.querySelector(s);
    if(mode==="equal") q("#splitInfo").textContent="Divisione 50 / 50";
    else if(mode==="payer") q("#splitInfo").textContent="100% a carico di chi ha pagato";
    else q("#splitInfo").textContent=`100% a carico di ${this.person(mode)}`;
  }

  buildShares(amount,payer){
    const members=this.members();
    const shares={};
    members.forEach(p=>shares[p.id]=0);

    if(this.splitMode==="payer"){
      shares[payer]=amount;
      return shares;
    }

    if(this.splitMode && this.splitMode!=="equal"){
      shares[this.splitMode]=amount;
      return shares;
    }

    if(members.length===2){
      const first=Math.round((amount/2)*100)/100;
      shares[members[0].id]=first;
      shares[members[1].id]=Math.round((amount-first)*100)/100;
      return shares;
    }

    if(!members.length) return shares;

    const each=Math.floor((amount/members.length)*100)/100;
    let assigned=0;
    members.forEach((p,i)=>{
      shares[p.id]=i===members.length-1 ? Math.round((amount-assigned)*100)/100 : each;
      assigned+=shares[p.id];
    });
    return shares;
  }

  async saveExpense(){
    const q=s=>this.shadowRoot.querySelector(s);
    try {
      const description=q("#d").value.trim();
      const amount=Number(q("#a").value);
      const payer=q("#payer").value;
      if(!description) throw new Error("Inserisci una descrizione");
      if(!amount || amount<=0) throw new Error("Inserisci un importo valido");

      await this.ws("fabios/add_expense",{
        description,
        amount,
        paid_by:payer,
        shares:this.buildShares(amount,payer),
        group_id:this.gid,
        category:"Altro",
        date:q("#dt").value,
        notes:"Inserita da Fabio’s Lite"
      });

      q("#expDlg").close();
      await this.load();
    } catch(e) {
      alert(e.message||e);
    }
  }

  openSettlement(){
    const b=this.currentBalance();
    const q=s=>this.shadowRoot.querySelector(s);
    if(b){
      q("#sf").value=b.from_person;
      q("#st").value=b.to_person;
      q("#sa").value=b.amount;
    }
    q("#setDlg").showModal();
  }

  async saveSettlement(){
    const q=s=>this.shadowRoot.querySelector(s);
    try {
      const from=q("#sf").value;
      const to=q("#st").value;
      const amount=Number(q("#sa").value);
      if(from===to) throw new Error("Scegli due persone diverse");
      if(!amount || amount<=0) throw new Error("Inserisci un importo valido");

      await this.ws("fabios/add_settlement",{
        from_person:from,
        to_person:to,
        amount,
        group_id:this.gid,
        date:q("#sd").value,
        notes:"Registrato da Fabio’s Lite"
      });

      q("#setDlg").close();
      await this.load();
    } catch(e) {
      alert(e.message||e);
    }
  }
}

if(!customElements.get("fabios-lite-panel")){
  customElements.define("fabios-lite-panel",FabiosLitePanel);
}
