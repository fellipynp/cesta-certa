const API = "";
let token = localStorage.getItem("cesta_token") || "";
let selectedFamily = null;
let families = [];
let searchTimer = null;

const $ = (id) => document.getElementById(id);
const authHeaders = () => ({Authorization: "Bearer " + token, "Content-Type": "application/json"});
async function api(path, options = {}) {
  const response = await fetch(API + path, {...options, headers: {...authHeaders(), ...(options.headers || {})}});
  const data = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (response.status === 401) { logout(); throw new Error("Sua sessão expirou. Entre novamente."); }
  if (!response.ok) throw new Error(data?.detail || "Não foi possível concluir a operação.");
  return data;
}
function showToast(message) { const el=$("toast"); el.textContent=message; el.classList.add("show"); setTimeout(()=>el.classList.remove("show"),2600); }
function setPage(page) {
  ["home","delivery","alerts"].forEach(name => $("page-"+name).classList.toggle("hidden", name!==page));
  document.querySelectorAll(".tab").forEach(tab=>tab.classList.toggle("active",tab.dataset.page===page));
  $("page-heading").textContent = ({home:"Menu inicial",delivery:"Registrar entrega",alerts:"Alertas e resultados"})[page];
  if(page==="home") loadDashboard();
  if(page==="delivery") loadFamilies($("family-search").value);
  if(page==="alerts") loadAlerts();
  window.scrollTo({top:0,behavior:"smooth"});
}
function openApp() { $("login-view").classList.add("hidden"); $("app-view").classList.remove("hidden"); setPage("home"); }
function logout() { token=""; selectedFamily=null; localStorage.removeItem("cesta_token"); $("app-view").classList.add("hidden"); $("login-view").classList.remove("hidden"); }
async function loadDashboard() {
  try {
    const [summary, alerts] = await Promise.all([api("/painel/resumo"),api("/estoque/alertas")]);
    $("home-month-title").textContent="Acompanhamento de "+summary.mes;
    $("home-count").textContent=summary.familias_atendidas+" de "+summary.total_familias+" famílias atendidas";
    $("home-percent").textContent=summary.percentual+"% concluído";
    $("home-progress").style.width=summary.percentual+"%";
    if(alerts.length){$("home-alert").textContent="⚠ Atenção: "+alerts.length+" item(ns) perto do vencimento. Acesse Alertas e resultados para conferir."; $("home-alert").classList.remove("hidden");}
    else $("home-alert").classList.add("hidden");
  } catch(error){showToast(error.message);}
}
async function loadFamilies(query="") {
  try {
    families=await api("/familias?busca="+encodeURIComponent(query));
    $("family-count").textContent=families.length+" resultado(s)";
    const list=$("family-results"); list.replaceChildren();
    if(!families.length){const p=document.createElement("p");p.className="muted";p.textContent="Nenhuma família encontrada.";list.append(p);return;}
    families.forEach(f=>{
      const card=document.createElement("button");card.type="button";card.className="family-card"+(selectedFamily?.id_familia===f.id_familia?" selected":"");
      const info=document.createElement("span");const name=document.createElement("span");name.className="family-name";name.textContent=f.nome_responsavel;
      const address=document.createElement("span");address.className="family-address";address.textContent=f.endereco;
      info.append(name,address);
      const status=document.createElement("span");status.className="status "+(f.status_mes==="recebeu"?"done":"pending");
      status.textContent=f.status_mes==="recebeu"?"Já recebeu em "+f.data_entrega:"Pendente";
      card.append(info,status);card.addEventListener("click",()=>selectFamily(f));list.append(card);
    });
  } catch(error){$("family-results").textContent=error.message;}
}
function selectFamily(f) {
  selectedFamily=f;$("selected-family").textContent=f.nome_responsavel+" · "+(f.status_mes==="recebeu"?"Já recebeu em "+f.data_entrega:"Entrega pendente");
  $("register-delivery").disabled=f.status_mes==="recebeu";
  $("delivery-message").textContent=f.status_mes==="recebeu"?"Esta família já recebeu a cesta neste mês.": "";
  $("delivery-message").className="message "+(f.status_mes==="recebeu"?"error":"");
  document.querySelectorAll(".family-card").forEach(card=>card.classList.remove("selected"));
  const index=families.findIndex(item=>item.id_familia===f.id_familia);$("family-results").children[index]?.classList.add("selected");
}
async function registerDelivery() {
  if(!selectedFamily)return;
  const button=$("register-delivery");button.disabled=true;button.textContent="Registrando...";
  try {
    const result=await api("/entregas",{method:"POST",body:JSON.stringify({id_familia:selectedFamily.id_familia})});
    $("delivery-message").textContent="Entrega registrada com sucesso em "+result.data_entrega+".";
    $("delivery-message").className="message success";selectedFamily=null;$("selected-family").textContent="Entrega concluída. Selecione outra família.";
    await loadFamilies($("family-search").value);loadDashboard();
    showToast("Entrega registrada com sucesso!");
  } catch(error){$("delivery-message").textContent=error.message;$("delivery-message").className="message error";}
  finally{button.textContent="Registrar entrega";button.disabled=!selectedFamily||selectedFamily.status_mes==="recebeu";}
}
async function loadAlerts() {
  try {
    const [items,summary]=await Promise.all([api("/estoque/alertas"),api("/painel/resumo")]);
    const list=$("stock-alerts");list.replaceChildren();
    if(!items.length){const p=document.createElement("p");p.className="muted panel";p.textContent="Nenhum item com vencimento nos próximos 15 dias.";list.append(p);}
    items.forEach(item=>{
      const card=document.createElement("div");card.className="family-card stock-item";
      const info=document.createElement("span");const name=document.createElement("strong");name.textContent=item.nome_produto;
      const detail=document.createElement("small");detail.textContent="Validade: "+item.data_validade+" · Saldo: "+item.quantidade+" "+item.unidade;
      info.append(name,detail);const days=document.createElement("span");days.className="days";days.textContent=item.dias_restantes===0?"Vence hoje":item.dias_restantes+" dias";card.append(info,days);list.append(card);
    });
    $("stat-attended").textContent=summary.familias_atendidas;
    $("stat-pending").textContent=summary.familias_pendentes;
    $("stat-deliveries").textContent=summary.cestas_entregues;
    $("stat-discarded").textContent=summary.itens_descartados;
    $("duplicate-alert").classList.add("hidden");
  } catch(error){showToast(error.message);}
}
$("login-form").addEventListener("submit",async event=>{
  event.preventDefault();$("login-error").textContent="";
  try {
    const response=await fetch("/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:$("email").value.trim(),senha:$("senha").value})});
    const data=await response.json().catch(()=>({}));
    if(!response.ok)throw new Error(data.detail||"Não foi possível entrar.");
    token=data.access_token;localStorage.setItem("cesta_token",token);openApp();
  } catch(error){$("login-error").textContent=error.message;}
});
$("logout").addEventListener("click",logout);
document.querySelectorAll("[data-page]").forEach(button=>button.addEventListener("click",()=>setPage(button.dataset.page)));
document.querySelectorAll("[data-go]").forEach(button=>button.addEventListener("click",()=>setPage(button.dataset.go)));
$("family-search").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadFamilies($("family-search").value),250);});
$("register-delivery").addEventListener("click",registerDelivery);
$("today-date").textContent=new Date().toLocaleDateString("pt-BR");
$("footer-year").textContent=new Date().toLocaleDateString("pt-BR",{month:"long",year:"numeric"});


// Preferências de acessibilidade salvas neste navegador.
const FONT_LEVELS = ["small", "normal", "large", "larger"];
let fontLevel = localStorage.getItem("cesta_font_level") || "normal";
let highContrast = localStorage.getItem("cesta_high_contrast") === "true";

function applyAccessibilitySettings() {
  document.documentElement.dataset.fontSize = FONT_LEVELS.includes(fontLevel) ? fontLevel : "normal";
  document.body.classList.toggle("high-contrast", highContrast);
  const contrastButton = $("contrast-toggle");
  contrastButton.setAttribute("aria-pressed", String(highContrast));
  contrastButton.textContent = highContrast ? "Alto contraste: ligado" : "Alto contraste: desligado";
}

function announceAccessibility(message) {
  $("accessibility-status").textContent = message;
}

$("contrast-toggle").addEventListener("click", () => {
  highContrast = !highContrast;
  localStorage.setItem("cesta_high_contrast", String(highContrast));
  applyAccessibilitySettings();
  announceAccessibility(highContrast ? "Modo de alto contraste ativado." : "Modo de alto contraste desativado.");
});

$("font-decrease").addEventListener("click", () => {
  const current = FONT_LEVELS.indexOf(fontLevel);
  fontLevel = FONT_LEVELS[Math.max(0, current - 1)];
  localStorage.setItem("cesta_font_level", fontLevel);
  applyAccessibilitySettings();
  announceAccessibility("Tamanho do texto ajustado.");
});

$("font-increase").addEventListener("click", () => {
  const current = FONT_LEVELS.indexOf(fontLevel);
  fontLevel = FONT_LEVELS[Math.min(FONT_LEVELS.length - 1, current + 1)];
  localStorage.setItem("cesta_font_level", fontLevel);
  applyAccessibilitySettings();
  announceAccessibility("Tamanho do texto ajustado.");
});

$("font-reset").addEventListener("click", () => {
  fontLevel = "normal";
  localStorage.setItem("cesta_font_level", fontLevel);
  applyAccessibilitySettings();
  announceAccessibility("Tamanho padrão do texto restaurado.");
});

applyAccessibilitySettings();

if(token)openApp();