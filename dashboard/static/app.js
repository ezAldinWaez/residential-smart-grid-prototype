"use strict";

const state = {
  snapshot: null,
  polling: false,
  history: [],
  houseFilter: "all",
  houseQuery: "",
  dialogHouse: null,
  dialogRequest: false,
  dialogPollTick: 0,
  toastTimer: null,
};

const numberFormat = new Intl.NumberFormat("ar-SY-u-nu-latn", { maximumFractionDigits: 2 });
const oneDecimalFormat = new Intl.NumberFormat("ar-SY-u-nu-latn", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const percentFormats = new Map();
const deviceLabels = {
  air_conditioner: "مكيّف الهواء",
  water_heater: "سخّان المياه",
  lighting: "الإنارة",
  refrigerator: "الثلاجة",
  washing_machine: "الغسالة",
  dishwasher: "غسالة الصحون",
  television: "التلفاز",
  computer: "الحاسوب",
  oven: "الفرن",
  microwave: "الميكروويف",
  fan: "المروحة",
  general_load: "الأحمال العامة",
};

function $(selector, parent = document) {
  return parent.querySelector(selector);
}

function $$(selector, parent = document) {
  return [...parent.querySelectorAll(selector)];
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function makeIcon(name) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", `#icon-${name}`);
  svg.append(use);
  return svg;
}

function formatPower(watts) {
  const value = Number(watts) || 0;
  if (Math.abs(value) >= 1000) return `${numberFormat.format(value / 1000)} kW`;
  return `${numberFormat.format(value)} W`;
}

function formatEnergy(wattHours) {
  const value = Number(wattHours) || 0;
  if (Math.abs(value) >= 1000) return `${oneDecimalFormat.format(value / 1000)} kWh`;
  return `${numberFormat.format(value)} Wh`;
}

function formatPercent(ratio, digits = 0) {
  if (!percentFormats.has(digits)) {
    percentFormats.set(digits, new Intl.NumberFormat("ar-SY-u-nu-latn", {
      style: "percent",
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }));
  }
  return percentFormats.get(digits).format(Number(ratio) || 0);
}

function humanize(value) {
  return deviceLabels[value] || String(value).replaceAll("_", " ");
}

function direction(value, positive, negative, neutral = "متوازن") {
  if (value > 0.01) return positive;
  if (value < -0.01) return negative;
  return neutral;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = { error: "أعاد الخادم استجابة غير صالحة." };
  }
  if (!response.ok || payload.ok === false) {
    throw new Error(`تعذّر إكمال الطلب. رمز الاستجابة ${numberFormat.format(response.status)}.`);
  }
  return payload;
}

function announce(message, tone = "default") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.dataset.tone = tone;
  toast.hidden = false;
  window.clearTimeout(state.toastTimer);
  state.toastTimer = window.setTimeout(() => { toast.hidden = true; }, 4200);
}

function setButtonBusy(button, busy) {
  button.disabled = busy;
  button.setAttribute("aria-busy", String(busy));
}

async function performAction(button, operation, successMessage) {
  setButtonBusy(button, true);
  try {
    await operation();
    if (successMessage) announce(successMessage);
    await refreshSnapshot();
  } catch (error) {
    announce(error.message, "error");
  } finally {
    setButtonBusy(button, false);
  }
}

function setConnectionStatus(connected) {
  document.getElementById("connection-banner").hidden = connected;
  if (connected) return;
  $$('[data-running-label]').forEach((element) => { element.textContent = "غير متصل"; });
  $$('[data-status-dot]').forEach((dot) => {
    dot.classList.remove("is-running", "is-paused");
    dot.classList.add("is-offline");
  });
  const verdict = document.getElementById("system-verdict");
  verdict.className = "verdict verdict-warning";
  verdict.querySelector("strong").textContent = "انقطع الاتصال";
  setText("system-narrative", "القياسات غير متاحة مؤقتاً. ستبقى عناصر التحكم محفوظة أثناء إعادة المحاولة.");
}

function renderRunningState(running) {
  const label = running ? "المحاكاة قيد التشغيل" : "المحاكاة متوقفة مؤقتاً";
  $$('[data-running-label]').forEach((element) => { element.textContent = label; });
  $$('[data-status-dot]').forEach((dot) => {
    dot.classList.remove("is-running", "is-paused", "is-offline");
    dot.classList.add(running ? "is-running" : "is-paused");
  });
  const toggle = document.getElementById("simulation-toggle");
  toggle.replaceChildren(makeIcon(running ? "pause" : "play"));
  const text = document.createElement("span");
  text.textContent = running ? "إيقاف مؤقت" : "متابعة";
  toggle.append(text);
  toggle.setAttribute("aria-label", running ? "إيقاف المحاكاة مؤقتاً" : "متابعة المحاكاة");
}

function renderTimestamp(timestamp) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    setText("simulation-clock", String(timestamp).slice(11, 19) || "--:--:--");
    setText("simulation-date", "وقت المحاكاة");
  } else {
    setText("simulation-clock", new Intl.DateTimeFormat("ar-SY-u-nu-latn", {
      hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
    }).format(date));
    setText("simulation-date", new Intl.DateTimeFormat("ar-SY-u-nu-latn", {
      day: "2-digit", month: "short", year: "numeric",
    }).format(date));
  }
  $$('[data-last-updated]').forEach((element) => { element.textContent = "حُدّث الآن"; });
}

function collectIssues(snapshot) {
  const issues = [];
  const houses = snapshot.houses.houses || [];
  const disconnectedUtilities = houses.filter((house) => !house.utility_line).length;
  const disabledLoads = houses.filter((house) => !house.load_line).length;
  const depleted = (snapshot.power.batteries || []).filter((battery) => Number(battery.state_of_charge) <= 0.05).length;

  if (!snapshot.running) issues.push({ tone: "warning", icon: "pause", title: "المحاكاة متوقفة مؤقتاً", detail: "تابع التشغيل عندما تكون جاهزاً لتقديم وقت النظام." });
  if (!snapshot.solar.running) issues.push({ tone: "warning", icon: "sun", title: "خدمة الطاقة الشمسية متوقفة", detail: "لن تتقدم قيم التوليد حتى متابعة المحاكاة." });
  if (!snapshot.power.running) issues.push({ tone: "warning", icon: "battery", title: "خدمة التوزيع متوقفة", detail: "لا تجري إعادة حساب الاحتياطيات الافتراضية." });
  if (!snapshot.solar.utility_line) issues.push({ tone: "danger", icon: "grid", title: "خط الشبكة العامة مفصول", detail: "لا يمكن للمنظومة استيراد الطاقة أو تصديرها." });
  if (Number(snapshot.solar.battery_soc) < 0.2) issues.push({ tone: "warning", icon: "battery", title: "الاحتياطي الفعلي منخفض", detail: `المتبقي ${formatPercent(snapshot.solar.battery_soc)} من سعة البطارية.` });
  if (disconnectedUtilities) issues.push({ tone: "warning", icon: "grid", title: `${numberFormat.format(disconnectedUtilities)} منازل معزولة عن الشبكة`, detail: "راجع المنازل المتأثرة ضمن عمليات المجتمع." });
  if (disabledLoads) issues.push({ tone: "warning", icon: "home", title: `${numberFormat.format(disabledLoads)} من أحمال المنازل معطّلة`, detail: "يجري فصل الطلب النموذجي عن هذه المنازل." });
  if (depleted) issues.push({ tone: "danger", icon: "battery", title: `${numberFormat.format(depleted)} من الاحتياطيات الافتراضية مستنفدة`, detail: "افتح البيانات الهندسية لفحص التوزيع حسب المنزل." });
  return issues;
}

function makeAttentionItem(issue) {
  const item = document.createElement("article");
  item.className = `attention-item is-${issue.tone}`;
  const icon = document.createElement("span");
  icon.append(makeIcon(issue.icon));
  const copy = document.createElement("span");
  const title = document.createElement("strong");
  title.textContent = issue.title;
  const detail = document.createElement("small");
  detail.textContent = issue.detail;
  copy.append(title, detail);
  item.append(icon, copy);
  return item;
}

function renderAttention(snapshot, issues) {
  const list = document.getElementById("attention-list");
  list.replaceChildren();
  if (!issues.length) {
    list.append(makeAttentionItem({ tone: "good", icon: "check", title: "لا يلزم أي تدخل", detail: "الخدمات ووصلات المنازل تعمل بصورة طبيعية." }));
  } else {
    issues.slice(0, 5).forEach((issue) => list.append(makeAttentionItem(issue)));
  }
  setText("attention-count", numberFormat.format(issues.length));

  const serviceStates = { houses: snapshot.houses.running, solar: snapshot.solar.running, power: snapshot.power.running };
  Object.entries(serviceStates).forEach(([service, running]) => {
    const element = document.querySelector(`[data-service="${service}"]`);
    element.classList.toggle("is-running", Boolean(running));
    element.title = `الخدمة ${running ? "قيد التشغيل" : "متوقفة مؤقتاً"}`;
  });
}

function renderAssessment(snapshot, issues) {
  const verdict = document.getElementById("system-verdict");
  const verdictText = verdict.querySelector("strong");
  const houses = snapshot.houses.houses || [];
  const enabled = houses.filter((house) => house.load_line).length;
  const balance = Number(snapshot.solar.solar_power) - Number(snapshot.houses.system_load);
  if (!issues.length) {
    verdict.className = "verdict verdict-good";
    verdictText.textContent = "التوزيع مستقر";
    setText("system-narrative", `يوزّع RSGP الطاقة الشمسية والاحتياطي المشترك على ${numberFormat.format(enabled)} منازل. ${balance >= 0 ? "يغطي التوليد الشمسي الطلب الحالي مع وجود فائض." : "تدعم البطارية والشبكة العامة التوليد الشمسي."}`);
  } else {
    verdict.className = "verdict verdict-warning";
    verdictText.textContent = `${numberFormat.format(issues.length)} حالات تؤثر في التوزيع`;
    setText("system-narrative", `يدير RSGP أحمال ${numberFormat.format(houses.length)} منازل عبر البطارية المشتركة؛ ${numberFormat.format(enabled)} أحمال مفعّلة حالياً. راجع القيود المؤثرة في عدالة التوزيع.`);
  }
}

function renderSignals(snapshot) {
  const { houses, solar } = snapshot;
  const rows = houses.houses || [];
  const enabledLoads = rows.filter((house) => house.load_line).length;
  const utilityConnections = rows.filter((house) => house.utility_line).length;
  const batteryState = direction(solar.battery_exchange_power, "قيد الشحن", "قيد التفريغ", "خاملة");
  const utilityState = direction(solar.utility_exchange_power, "تصدير", "استيراد", "متوازنة");

  setText("metric-solar", formatPower(solar.solar_power));
  setText("metric-solar-meta", `${numberFormat.format(solar.panel_count)} لوحاً · ${solar.running ? "مباشر" : "متوقف"}`);
  setText("metric-demand", formatPower(houses.system_load));
  setText("metric-demand-meta", `${numberFormat.format(enabledLoads)} من ${numberFormat.format(rows.length)} أحمال مفعّلة`);
  setText("metric-battery", formatPercent(solar.battery_soc));
  setText("metric-battery-meta", `${batteryState} · المتاح ${formatEnergy(solar.battery_residual)}`);
  setText("metric-utility", formatPower(Math.abs(solar.utility_exchange_power)));
  setText("metric-utility-meta", `${utilityState} · ${numberFormat.format(utilityConnections)} منازل متصلة`);
}

function renderFlow(snapshot) {
  const { houses, solar } = snapshot;
  const rows = houses.houses || [];
  const batteryState = direction(solar.battery_exchange_power, "قيد الشحن", "قيد التفريغ", "خاملة");
  const utilityState = direction(solar.utility_exchange_power, "تصدير", "استيراد", "متوازنة");
  const balance = Number(solar.solar_power) - Number(houses.system_load);

  setText("flow-solar", formatPower(solar.solar_power));
  setText("flow-demand", formatPower(houses.system_load));
  setText("flow-battery", formatPower(Math.abs(solar.battery_exchange_power)));
  setText("flow-utility", formatPower(Math.abs(solar.utility_exchange_power)));
  setText("flow-solar-state", Number(solar.solar_power) > 0 ? "قيد التوليد" : "خاملة");
  setText("flow-homes-state", `${numberFormat.format(rows.filter((house) => house.load_line).length)} أحمال مفعّلة`);
  setText("flow-battery-state", `البطارية · ${batteryState}`);
  setText("flow-utility-state", `الشبكة · ${utilityState}`);

  const chip = document.getElementById("flow-balance-chip");
  if (Math.abs(balance) < 10) {
    chip.textContent = "التغذية متوازنة";
    chip.className = "status-badge is-good";
  } else if (balance > 0) {
    chip.textContent = "فائض شمسي";
    chip.className = "status-badge is-good";
  } else {
    chip.textContent = "التغذية المساندة فعّالة";
    chip.className = "status-badge is-warning";
  }

  const solarPhrase = `يوجّه RSGP توليداً شمسياً قدره ${formatPower(solar.solar_power)} لخدمة طلب سكني قدره ${formatPower(houses.system_load)}.`;
  const supportPhrase = batteryState === "خاملة" && utilityState === "متوازنة"
    ? "لا يوجد تبادل مساند فعّال."
    : `البطارية ${batteryState} باستطاعة ${formatPower(Math.abs(solar.battery_exchange_power))}، والشبكة في حالة ${utilityState} باستطاعة ${formatPower(Math.abs(solar.utility_exchange_power))}.`;
  setText("flow-summary", `${solarPhrase} ${supportPhrase}`);

  state.history.push(Number(houses.system_load) || 0);
  if (state.history.length > 60) state.history.shift();
  renderDemandChart();
}

function renderDemandChart() {
  const samples = state.history;
  if (!samples.length) return;
  const width = 720;
  const height = 132;
  const padding = 10;
  const maximum = Math.max(...samples, 1) * 1.12;
  const points = samples.map((value, index) => {
    const x = samples.length === 1 ? width : (index / (samples.length - 1)) * width;
    const y = height - padding - (value / maximum) * (height - padding * 2);
    return [x, y];
  });
  const line = points.map(([x, y], index) => `${index === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`).join(" ");
  const area = `${line} L${points.at(-1)[0].toFixed(2)} ${height} L${points[0][0].toFixed(2)} ${height} Z`;
  document.getElementById("demand-line").setAttribute("d", line);
  document.getElementById("demand-area").setAttribute("d", area);
  setText("trend-current", formatPower(samples.at(-1)));

  const delta = samples.length > 1 ? samples.at(-1) - samples[0] : 0;
  const trend = delta > 0 ? "ازداد" : delta < 0 ? "انخفض" : "بقي مستقراً";
  document.getElementById("trend-summary").textContent = `${numberFormat.format(samples.length)} عينة للطلب. الطلب الحالي ${formatPower(samples.at(-1))} وقد ${trend}${delta ? ` بمقدار ${formatPower(Math.abs(delta))}` : ""} خلال الفترة الظاهرة.`;
}

function buildHouseRow(house) {
  const row = document.createElement("article");
  row.className = "house-row";
  row.dataset.houseIdx = String(house.idx);

  const identity = document.createElement("div");
  identity.className = "house-identity";
  const icon = document.createElement("span");
  icon.className = "house-icon";
  icon.append(makeIcon("home"));
  const identityCopy = document.createElement("span");
  const title = document.createElement("strong");
  title.textContent = `المنزل ${numberFormat.format(house.idx + 1)}`;
  const status = document.createElement("small");
  status.dataset.role = "house-status";
  identityCopy.append(title, status);
  identity.append(icon, identityCopy);

  const demand = document.createElement("div");
  demand.className = "house-demand";
  const demandValue = document.createElement("strong");
  demandValue.dataset.role = "house-load";
  const demandShare = document.createElement("small");
  demandShare.dataset.role = "house-share";
  const demandBar = document.createElement("div");
  demandBar.className = "demand-bar";
  demandBar.setAttribute("aria-hidden", "true");
  demandBar.append(document.createElement("span"));
  demand.append(demandValue, demandShare, demandBar);

  const lineButtons = ["utility", "load"].map((line) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "line-control";
    button.dataset.houseLine = line;
    const label = document.createElement("span");
    label.dataset.role = "line-label";
    const track = document.createElement("span");
    track.className = "switch-track";
    track.setAttribute("aria-hidden", "true");
    button.append(label, track);
    button.addEventListener("click", () => toggleHouseLine(button, house.idx, line));
    return button;
  });

  const devices = document.createElement("button");
  devices.type = "button";
  devices.className = "button button-secondary device-button";
  devices.append(makeIcon("sliders"), document.createTextNode("فتح"));
  devices.setAttribute("aria-label", `فتح تحكم أجهزة المنزل ${numberFormat.format(house.idx + 1)}`);
  devices.addEventListener("click", () => openDeviceDialog(house.idx));

  row.append(identity, demand, ...lineButtons, devices);
  return row;
}

function updateHouseRow(row, house, total, peak) {
  const operational = house.load_line && house.utility_line;
  const status = !house.load_line ? "الحمل معطّل" : !house.utility_line ? "معزول عن الشبكة" : "تشغيل طبيعي";
  const share = total ? Number(house.load) / total : 0;
  row.classList.toggle("needs-attention", !operational);
  row.dataset.attention = String(!operational);
  row.dataset.search = `منزل البيت ${numberFormat.format(house.idx + 1)} ${house.idx + 1} ${status}`.toLowerCase();
  row.querySelector('[data-role="house-status"]').textContent = status;
  row.querySelector('[data-role="house-load"]').textContent = formatPower(house.load);
  row.querySelector('[data-role="house-share"]').textContent = `${formatPercent(share, 1)} من طلب المجتمع`;
  row.querySelector(".demand-bar span").style.width = `${peak ? Math.min(100, (Number(house.load) / peak) * 100) : 0}%`;

  ["utility", "load"].forEach((line) => {
    const connected = Boolean(house[`${line}_line`]);
    const button = row.querySelector(`[data-house-line="${line}"]`);
    button.setAttribute("aria-pressed", String(connected));
    button.setAttribute("aria-label", `${connected ? "فصل" : "وصل"} خط ${line === "utility" ? "الشبكة" : "الحمل"} للمنزل ${numberFormat.format(house.idx + 1)}`);
    button.querySelector('[data-role="line-label"]').textContent = `${line === "utility" ? "الشبكة" : "الحمل"} ${connected ? "متصل" : "مفصول"}`;
  });
}

function renderHouses(metrics) {
  const houses = metrics.houses || [];
  const total = Number(metrics.system_load) || 0;
  const peak = Math.max(...houses.map((house) => Number(house.load) || 0), 0);
  const online = houses.filter((house) => house.load_line && house.utility_line).length;
  const list = document.getElementById("house-list");
  const present = new Set(houses.map((house) => String(house.idx)));

  $$(".house-row", list).forEach((row) => {
    if (!present.has(row.dataset.houseIdx)) row.remove();
  });
  houses.forEach((house) => {
    let row = list.querySelector(`[data-house-idx="${house.idx}"]`);
    if (!row) {
      row = buildHouseRow(house);
      list.append(row);
    }
    updateHouseRow(row, house, total, peak);
  });

  setText("houses-total-demand", formatPower(total));
  setText("houses-online", `${numberFormat.format(online)}/${numberFormat.format(houses.length)}`);
  setText("house-attention-count", numberFormat.format(houses.length - online));
  applyHouseFilter();
}

function applyHouseFilter() {
  const query = state.houseQuery.trim().toLowerCase();
  let visible = 0;
  $$(".house-row", document.getElementById("house-list")).forEach((row) => {
    const matchesFilter = state.houseFilter === "all" || row.dataset.attention === "true";
    const matchesQuery = !query || row.dataset.search.includes(query);
    row.hidden = !(matchesFilter && matchesQuery);
    if (!row.hidden) visible += 1;
  });
  document.getElementById("house-empty").hidden = visible !== 0;
}

async function toggleHouseLine(button, houseIdx, line) {
  await performAction(
    button,
    () => api(`/api/houses/${houseIdx}/lines/${line}/toggle`, { method: "POST" }),
    `تم تحديث خط ${line === "utility" ? "الشبكة" : "الحمل"} للمنزل ${numberFormat.format(houseIdx + 1)}.`,
  );
}

function ensureRow(tbody, id, cells) {
  let row = tbody.querySelector(`[data-row-id="${id}"]`);
  if (!row) {
    row = document.createElement("tr");
    row.dataset.rowId = id;
    cells.forEach(() => row.append(document.createElement("td")));
    tbody.append(row);
  }
  cells.forEach((cell, index) => {
    row.children[index].textContent = cell.text;
    row.children[index].className = cell.className || "";
  });
}

function renderEngineering(snapshot) {
  const metrics = snapshot.solar;
  const batteryState = direction(metrics.battery_exchange_power, "قيد الشحن", "قيد التفريغ", "خاملة");
  const utilityState = direction(metrics.utility_exchange_power, "تصدير", "استيراد", "متوازنة");
  const service = document.getElementById("solar-service-state");
  service.textContent = metrics.running ? "الخدمة قيد التشغيل" : "الخدمة متوقفة";
  service.className = `status-badge ${metrics.running ? "is-good" : "is-warning"}`;
  setText("solar-output", formatPower(metrics.solar_power));
  setText("solar-output-meta", `${numberFormat.format(metrics.panel_count)} لوحاً`);
  setText("solar-battery-power", formatPower(Math.abs(metrics.battery_exchange_power)));
  setText("solar-battery-state", batteryState);
  setText("solar-utility-power", formatPower(Math.abs(metrics.utility_exchange_power)));
  setText("solar-utility-state", `${utilityState} · ${metrics.utility_line ? "متصلة" : "مفصولة"}`);

  const progress = document.getElementById("solar-reserve-progress");
  const percentage = Math.max(0, Math.min(100, Number(metrics.battery_soc) * 100));
  progress.setAttribute("aria-valuenow", percentage.toFixed(0));
  progress.querySelector("span").style.width = `${percentage}%`;
  setText("solar-reserve-label", `${formatPercent(percentage / 100)} · ${formatEnergy(metrics.battery_residual)}`);
  setText("config-mode", metrics.inverter_mode);
  setText("config-priority", metrics.charge_priority);
  setText("config-array", `${numberFormat.format(metrics.panel_count)} × ${oneDecimalFormat.format(metrics.panel_area)} م² بكفاءة ${formatPercent(metrics.panel_efficiency)}`);
  setText("config-inverter", formatPower(metrics.inverter_rated_power));
  setText("config-battery", `شحن ${formatPower(metrics.battery_max_charge_power)} · تفريغ ${formatPower(metrics.battery_max_discharge_power)}`);

  const power = snapshot.power;
  const batteries = power.batteries || [];
  const weights = batteries.map((battery) => Number(battery.weight));
  setText("allocation-capacity", formatEnergy(power.total_capacity));
  setText("allocation-reserve", formatEnergy(power.residual_capacity));
  setText("allocation-soc", formatPercent(power.state_of_charge));
  setText("allocation-range", weights.length ? `${numberFormat.format(Math.min(...weights))}–${numberFormat.format(Math.max(...weights))}` : "—");

  const tbody = document.getElementById("allocation-body");
  const present = new Set(batteries.map((battery) => `battery-${battery.idx}`));
  $$('tr[data-row-id]', tbody).forEach((row) => { if (!present.has(row.dataset.rowId)) row.remove(); });
  batteries.forEach((battery) => {
    const reserveState = battery.state_of_charge <= 0.05 ? "مستنفد" : battery.state_of_charge < 0.2 ? "منخفض" : "متاح";
    ensureRow(tbody, `battery-${battery.idx}`, [
      { text: `المنزل ${numberFormat.format(battery.idx + 1)}` },
      { text: numberFormat.format(Number(battery.weight)) },
      { text: formatEnergy(battery.total_capacity) },
      { text: formatEnergy(battery.residual_capacity) },
      { text: `${formatPercent(battery.state_of_charge, 1)} · ${reserveState}`, className: reserveState === "متاح" ? "cell-state is-good" : reserveState === "منخفض" ? "cell-state is-warning" : "cell-state is-danger" },
    ]);
  });
}

function renderSnapshot(snapshot) {
  state.snapshot = snapshot;
  setConnectionStatus(true);
  renderRunningState(snapshot.running);
  renderTimestamp(snapshot.timestamp);
  const issues = collectIssues(snapshot);
  renderAssessment(snapshot, issues);
  renderSignals(snapshot);
  renderFlow(snapshot);
  renderAttention(snapshot, issues);
  renderHouses(snapshot.houses);
  renderEngineering(snapshot);
}

async function refreshSnapshot() {
  if (state.polling || document.hidden) return;
  state.polling = true;
  try {
    const snapshot = await api("/api/snapshot", { headers: {} });
    renderSnapshot(snapshot);
    if (document.getElementById("device-dialog").open) {
      state.dialogPollTick += 1;
      if (state.dialogPollTick % 2 === 0) refreshDeviceDialog();
    }
  } catch {
    setConnectionStatus(false);
  } finally {
    state.polling = false;
  }
}

async function openDeviceDialog(houseIdx) {
  state.dialogHouse = houseIdx;
  state.dialogPollTick = 0;
  setText("device-dialog-title", `المنزل ${numberFormat.format(houseIdx + 1)}`);
  setText("dialog-house-load", "—");
  const list = document.getElementById("device-list");
  list.replaceChildren();
  const loading = document.createElement("p");
  loading.className = "empty-state";
  loading.textContent = "جارٍ تحميل عناصر تحكم الأجهزة…";
  list.append(loading);
  document.getElementById("device-dialog").showModal();
  await refreshDeviceDialog();
}

async function refreshDeviceDialog() {
  if (state.dialogHouse === null || state.dialogRequest) return;
  state.dialogRequest = true;
  try {
    const metrics = await api(`/api/houses/${state.dialogHouse}/devices`, { headers: {} });
    renderDeviceDialog(metrics);
  } catch (error) {
    const list = document.getElementById("device-list");
    list.replaceChildren();
    const message = document.createElement("p");
    message.className = "empty-state";
    message.textContent = error.message;
    list.append(message);
  } finally {
    state.dialogRequest = false;
  }
}

function renderDeviceDialog(metrics) {
  setText("dialog-house-load", formatPower(metrics.load));
  const utility = document.getElementById("dialog-utility-state");
  utility.textContent = `الشبكة ${metrics.utility_line ? "متصلة" : "مفصولة"}`;
  utility.className = `status-badge ${metrics.utility_line ? "is-good" : "is-warning"}`;
  const load = document.getElementById("dialog-load-state");
  load.textContent = `الحمل ${metrics.load_line ? "مفعّل" : "معطّل"}`;
  load.className = `status-badge ${metrics.load_line ? "is-good" : "is-warning"}`;

  const list = document.getElementById("device-list");
  $$(':scope > .empty-state', list).forEach((message) => message.remove());
  const existing = new Map($$(".device-card", list).map((card) => [card.dataset.deviceName, card]));
  const present = new Set(metrics.devices.map((device) => device.name));
  existing.forEach((card, name) => { if (!present.has(name)) card.remove(); });

  metrics.devices.forEach((device) => {
    let card = existing.get(device.name);
    if (!card) {
      card = document.createElement("article");
      card.className = "device-card";
      card.dataset.deviceName = device.name;
      const header = document.createElement("div");
      header.className = "device-card-header";
      const title = document.createElement("h3");
      title.textContent = humanize(device.name);
      const value = document.createElement("strong");
      value.dataset.role = "device-load";
      header.append(title, value);
      const controls = document.createElement("div");
      controls.className = "unit-controls";
      controls.dataset.role = "unit-controls";
      const details = document.createElement("details");
      details.className = "device-details";
      const summaryLabel = document.createElement("summary");
      summaryLabel.textContent = "الإعدادات الفنية";
      const summary = document.createElement("p");
      summary.dataset.role = "device-summary";
      details.append(summaryLabel, summary);
      card.append(header, controls, details);
      list.append(card);
    }

    card.querySelector('[data-role="device-load"]').textContent = formatPower(device.load);
    card.querySelector('[data-role="device-summary"]').textContent = device.summary;
    const controls = card.querySelector('[data-role="unit-controls"]');
    const envelopeIds = new Set(device.envelopes.map((envelope) => String(envelope.idx)));
    $$('[data-envelope-idx]', controls).forEach((button) => { if (!envelopeIds.has(button.dataset.envelopeIdx)) button.remove(); });
    device.envelopes.forEach((envelope) => {
      let button = controls.querySelector(`[data-envelope-idx="${envelope.idx}"]`);
      if (!button) {
        button = document.createElement("button");
        button.type = "button";
        button.className = "unit-button";
        button.dataset.envelopeIdx = String(envelope.idx);
        button.addEventListener("click", () => toggleDeviceUnit(button, metrics.house_idx, device.name, envelope.idx));
        controls.append(button);
      }
      button.textContent = `الوحدة ${numberFormat.format(envelope.idx + 1)} · ${envelope.active ? "تعمل" : "متوقفة"}`;
      button.setAttribute("aria-pressed", String(envelope.active));
      button.setAttribute("aria-label", `${envelope.active ? "إيقاف" : "تشغيل"} الوحدة ${numberFormat.format(envelope.idx + 1)} من ${humanize(device.name)}`);
    });
  });
}

async function toggleDeviceUnit(button, houseIdx, deviceName, envelopeIdx) {
  await performAction(
    button,
    () => api(`/api/houses/${houseIdx}/devices/${encodeURIComponent(deviceName)}/${envelopeIdx}/toggle`, { method: "POST" }),
    `تم تحديث الوحدة ${numberFormat.format(envelopeIdx + 1)} من ${humanize(deviceName)}.`,
  );
  await refreshDeviceDialog();
}

function bindActions() {
  document.getElementById("simulation-toggle").addEventListener("click", (event) => {
    performAction(
      event.currentTarget,
      () => api("/api/simulation/toggle", { method: "POST" }),
      state.snapshot?.running ? "تم إيقاف المحاكاة مؤقتاً." : "تمت متابعة المحاكاة.",
    );
  });

  document.getElementById("engineering-button").addEventListener("click", () => {
    document.getElementById("engineering-dialog").showModal();
  });

  document.getElementById("network-controls-button").addEventListener("click", () => {
    document.getElementById("network-dialog").showModal();
  });

  $$('[data-bulk-line]').forEach((button) => {
    button.addEventListener("click", () => {
      const line = button.dataset.bulkLine;
      const desiredState = button.dataset.state === "true";
      performAction(
        button,
        () => api(`/api/houses/lines/${line}`, { method: "POST", body: JSON.stringify({ state: desiredState }) }),
        `تم ${desiredState ? "وصل" : "فصل"} خطوط ${line === "utility" ? "الشبكة" : "الحمل"} لجميع المنازل.`,
      );
    });
  });

  $$('[data-close-dialog]').forEach((button) => {
    button.addEventListener("click", () => document.getElementById(button.dataset.closeDialog).close());
  });

  document.getElementById("device-dialog").addEventListener("close", () => { state.dialogHouse = null; });
  document.getElementById("house-search").addEventListener("input", (event) => {
    state.houseQuery = event.target.value;
    applyHouseFilter();
  });
  $$('[data-house-filter]').forEach((button) => {
    button.addEventListener("click", () => {
      state.houseFilter = button.dataset.houseFilter;
      $$('[data-house-filter]').forEach((candidate) => {
        const selected = candidate === button;
        candidate.classList.toggle("is-active", selected);
        candidate.setAttribute("aria-pressed", String(selected));
      });
      applyHouseFilter();
    });
  });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshSnapshot(); });
}

async function initialize() {
  bindActions();
  await refreshSnapshot();
  const directHouse = Number.parseInt(new URLSearchParams(window.location.search).get("house"), 10);
  if (Number.isInteger(directHouse) && directHouse >= 0) await openDeviceDialog(directHouse);
  window.setInterval(refreshSnapshot, 1000);
}

initialize();
