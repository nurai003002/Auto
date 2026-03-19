/* ═══════════════════════════════════════════════════════════════
   AutoTrack — Application Logic
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ──────────────────────────────────────────────────────────────
   DJANGO DATA (rendered server-side)
   ────────────────────────────────────────────────────────────── */
const DJANGO_DATA = JSON.parse(document.getElementById('django-data').textContent);

/* ──────────────────────────────────────────────────────────────
   API LAYER
   ────────────────────────────────────────────────────────────── */
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function apiFetch(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) headers['X-CSRFToken'] = csrfToken;
  return fetch(url, { ...options, headers }).then(r => {
    if (r.status === 204) return null;
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });
}

const API = {
  async getCar(id)              { return apiFetch(`/api/cars/${id}/`); },
  async createCar(data)         { return apiFetch('/api/cars/', { method: 'POST', body: JSON.stringify(data) }); },
  async updateCar(id, data)     { return apiFetch(`/api/cars/${id}/`, { method: 'PUT', body: JSON.stringify(data) }); },
  async deleteCar(id)           { return apiFetch(`/api/cars/${id}/`, { method: 'DELETE' }); },

  async getCars()               { return apiFetch('/api/cars/'); },
  async getRepairs()            { return apiFetch('/api/repairs/'); },
  async getRepairsForCar(carId) { return apiFetch('/api/repairs/').then(rs => rs.filter(r => r.car_id === carId)); },
  async createRepair(data)      { return apiFetch('/api/repairs/', { method: 'POST', body: JSON.stringify(data) }); },
  async updateRepair(id, data)  { return apiFetch(`/api/repairs/${id}/`, { method: 'PUT', body: JSON.stringify(data) }); },
  async deleteRepair(id)        { return apiFetch(`/api/repairs/${id}/`, { method: 'DELETE' }); },
};

/* ──────────────────────────────────────────────────────────────
   STATE
   ────────────────────────────────────────────────────────────── */
const State = {
  currentPage: 'dashboard',
  carFilter: 'all',
  reminderFilter: 'all',
  reportPreview: 'cars',
  confirmCallback: null,
};

/* ──────────────────────────────────────────────────────────────
   HELPERS
   ────────────────────────────────────────────────────────────── */
function today() { return new Date(); }

function getSeenAlertIds() {
  try { return new Set(JSON.parse(localStorage.getItem('seenAlertIds') || '[]')); }
  catch { return new Set(); }
}

function markAlertsAsSeen() {
  localStorage.setItem('seenAlertIds', JSON.stringify(DJANGO_DATA.alertReminderIds));
}

function parseDate(str) {
  if (!str) return null;
  const [y, m, d] = str.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function formatDate(str) {
  if (!str) return '—';
  return parseDate(str).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function getRepairStatus(nextDateStr) {
  if (!nextDateStr) return 'ok';
  const diff = Math.ceil((parseDate(nextDateStr) - today()) / 86400000);
  if (diff < 0) return 'overdue';
  if (diff <= 31) return 'soon';
  return 'ok';
}

function statusLabel(status) {
  return { ok: 'В норме', soon: 'Скоро', overdue: 'Просрочено' }[status];
}

function el(id) { return document.getElementById(id); }

/* ──────────────────────────────────────────────────────────────
   TOAST
   ────────────────────────────────────────────────────────────── */
const Toast = {
  show(msg, type = 'info', duration = 3500) {
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ'}</span>
                   <span class="toast-msg">${msg}</span>`;
    el('toastContainer').appendChild(t);
    setTimeout(() => {
      t.classList.add('removing');
      t.addEventListener('animationend', () => t.remove());
    }, duration);
  },
  success: (m) => Toast.show(m, 'success'),
  error:   (m) => Toast.show(m, 'error'),
  warning: (m) => Toast.show(m, 'warning'),
  info:    (m) => Toast.show(m, 'info'),
};

/* ──────────────────────────────────────────────────────────────
   SIDEBAR
   ────────────────────────────────────────────────────────────── */
function initSidebar() {
  el('sidebarToggle').addEventListener('click', () => {
    el('sidebar').classList.toggle('open');
    el('sidebarOverlay').classList.toggle('open');
  });
  el('sidebarOverlay').addEventListener('click', () => {
    el('sidebar').classList.remove('open');
    el('sidebarOverlay').classList.remove('open');
  });
}

/* ──────────────────────────────────────────────────────────────
   BADGES
   ────────────────────────────────────────────────────────────── */
function initBadges() {
  const seen = getSeenAlertIds();
  const unseen = DJANGO_DATA.alertReminderIds.filter(id => !seen.has(id)).length;

  const rb = el('nav-badge-reminders');
  rb.textContent = unseen;
  rb.style.display = unseen ? '' : 'none';

  const tb = el('topNotifBadge');
  tb.textContent = unseen;

  const cb = el('nav-badge-cars');
  cb.style.display = DJANGO_DATA.totalCars ? '' : 'none';
}

/* ──────────────────────────────────────────────────────────────
   NAVIGATION
   ────────────────────────────────────────────────────────────── */
const pageTitles = {
  dashboard: 'Панель управления',
  cars:      'Автомобили',
  repairs:   'Ремонты',
  reminders: 'Напоминания',
  reports:   'Отчёты',
};

const App = {
  navigate(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    el(`page-${page}`).classList.add('active');
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');

    State.currentPage = page;
    el('pageTitle').textContent = pageTitles[page] || page;

    el('sidebar').classList.remove('open');
    el('sidebarOverlay').classList.remove('open');

    if (page === 'reminders') {
      markAlertsAsSeen();
      el('nav-badge-reminders').textContent = '0';
      el('nav-badge-reminders').style.display = 'none';
      el('topNotifBadge').textContent = '0';
    }

    if (page === 'reports') this.renderReport(State.reportPreview);
  },

  /* ── CARS filter (DOM-based) ── */
  filterCars() {
    const search = (el('carsSearch')?.value || '').toLowerCase();
    const filter = State.carFilter;

    document.querySelectorAll('#carsTbody tr:not(.empty-row)').forEach(row => {
      const brand = (row.dataset.brand || '').toLowerCase();
      const model = (row.dataset.model || '').toLowerCase();
      const plate = (row.dataset.plate || '').toLowerCase();
      const status = row.dataset.status || 'ok';

      const matchSearch = !search || brand.includes(search) || model.includes(search) || plate.includes(search);
      const matchFilter = filter === 'all' ||
        (filter === 'attention' && status !== 'ok') ||
        (filter === 'ok' && status === 'ok');

      row.style.display = matchSearch && matchFilter ? '' : 'none';
    });
  },

  setCarFilter(f, btn) {
    State.carFilter = f;
    document.querySelectorAll('#carsFilter .filter-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    this.filterCars();
  },

  /* ── REPAIRS filter (DOM-based) ── */
  filterRepairs() {
    const search = (el('repairsSearch')?.value || '').toLowerCase();
    const carFilterVal = el('repairsCarFilter')?.value || '';

    document.querySelectorAll('#repairsTbody tr:not(.empty-row)').forEach(row => {
      const searchText = (row.dataset.search || '').toLowerCase();
      const carId = row.dataset.carId || '';

      const matchSearch = !search || searchText.includes(search);
      const matchCar = !carFilterVal || carId === carFilterVal;

      row.style.display = matchSearch && matchCar ? '' : 'none';
    });
  },

  /* ── REMINDERS filter (DOM-based) ── */
  setReminderFilter(f, btn) {
    State.reminderFilter = f;
    document.querySelectorAll('.reminders-filters .filter-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('#remindersList .reminder-card').forEach(card => {
      const status = card.dataset.status || '';
      card.style.display = (f === 'all' || status === f) ? '' : 'none';
    });
  },

  /* ── REPORTS (still JS-rendered) ── */
  async renderReport(type) {
    const [cars, repairs] = await Promise.all([API.getCars(), API.getRepairs()]);
    State.reportPreview = type;
    const wrap = el('reportPreviewWrap');

    if (type === 'cars') {
      wrap.innerHTML = `<table class="data-table">
        <thead><tr><th>Марка</th><th>Модель</th><th>Гос. номер</th><th>Год</th><th>Примечание</th></tr></thead>
        <tbody>${cars.map(c => `<tr>
          <td>${c.brand}</td><td>${c.model}</td>
          <td class="font-mono">${c.plate}</td><td>${c.year}</td>
          <td class="text-muted">${c.note || '—'}</td>
        </tr>`).join('')}</tbody>
      </table>`;
    } else if (type === 'repairs') {
      const carMap = {};
      cars.forEach(c => carMap[c.id] = c);
      wrap.innerHTML = `<table class="data-table">
        <thead><tr><th>Автомобиль</th><th>Тип</th><th>Дата</th><th>Следующий ремонт</th><th>Комментарий</th></tr></thead>
        <tbody>${[...repairs].sort((a,b) => b.date.localeCompare(a.date)).map(r => {
          const c = carMap[r.car_id];
          return `<tr>
            <td>${c ? `${c.brand} ${c.model}` : '—'}</td>
            <td><span class="repair-type">${r.type}</span></td>
            <td>${formatDate(r.date)}</td>
            <td>${formatDate(r.next_date)}</td>
            <td class="text-muted">${r.comment || '—'}</td>
          </tr>`;
        }).join('')}</tbody>
      </table>`;
    } else {
      const carMap = {};
      cars.forEach(c => carMap[c.id] = c);
      const upcoming = repairs.filter(r => r.next_date).sort((a,b) => a.next_date.localeCompare(b.next_date)).slice(0, 20);
      wrap.innerHTML = `<table class="data-table">
        <thead><tr><th>Автомобиль</th><th>Тип ремонта</th><th>Дата ремонта</th><th>Статус</th></tr></thead>
        <tbody>${upcoming.map(r => {
          const c = carMap[r.car_id];
          const st = getRepairStatus(r.next_date);
          return `<tr>
            <td>${c ? `${c.brand} ${c.model} (${c.plate})` : '—'}</td>
            <td><span class="repair-type">${r.type}</span></td>
            <td><strong>${formatDate(r.next_date)}</strong></td>
            <td><span class="status-badge ${st}">${statusLabel(st)}</span></td>
          </tr>`;
        }).join('')}</tbody>
      </table>`;
    }
  },

  setReportPreview(type, btn) {
    document.querySelectorAll('.report-type-tabs .filter-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    this.renderReport(type);
  },

  exportReport(type, format) {
    const a = document.createElement('a');
    a.href = `/api/reports/${type}/export/${format}/`;
    a.download = `autotrack_${type}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  },

  /* ── CAR MODAL ── */
  openCarModal(id = null) {
    el('carModalTitle').textContent = id ? 'Редактировать автомобиль' : 'Добавить автомобиль';
    el('carId').value = id || '';
    el('carForm').reset();
    el('carId').value = id || '';

    if (id) {
      API.getCar(id).then(car => {
        if (!car) return;
        el('carBrand').value = car.brand;
        el('carModel').value = car.model;
        el('carPlate').value = car.plate;
        el('carYear').value  = car.year;
        el('carNote').value  = car.note || '';
      });
    }
    this._openModal('carModalBackdrop');
  },

  closeCarModal() { this._closeModal('carModalBackdrop'); },

  async saveCar(e) {
    e.preventDefault();
    const data = {
      brand: el('carBrand').value.trim(),
      model: el('carModel').value.trim(),
      plate: el('carPlate').value.trim(),
      year:  parseInt(el('carYear').value),
      note:  el('carNote').value.trim(),
    };
    const id = el('carId').value ? parseInt(el('carId').value) : null;
    try {
      if (id) {
        await API.updateCar(id, data);
      } else {
        await API.createCar(data);
      }
      window.location.reload();
    } catch {
      Toast.error('Ошибка сохранения');
    }
  },

  confirmDeleteCar(id) {
    el('confirmText').textContent = 'Удалить автомобиль и все его ремонты? Это действие нельзя отменить.';
    State.confirmCallback = async () => {
      await API.deleteCar(id);
      window.location.reload();
    };
    this._openModal('confirmModalBackdrop');
  },

  /* ── REPAIR MODAL ── */
  async openRepairModal(id = null, presetCarId = null) {
    el('repairModalTitle').textContent = id ? 'Редактировать ремонт' : 'Добавить ремонт';
    el('repairForm').reset();
    el('repairId').value = id || '';

    const cars = await API.getCars();
    const sel = el('repairCarId');
    sel.innerHTML = '<option value="">Выберите автомобиль…</option>' +
      cars.map(c => `<option value="${c.id}">${c.brand} ${c.model} (${c.plate})</option>`).join('');

    if (presetCarId) sel.value = presetCarId;
    el('repairDate').value = today().toISOString().slice(0, 10);

    if (id) {
      const repairs = await API.getRepairs();
      const r = repairs.find(x => x.id === id);
      if (r) {
        sel.value = r.car_id;
        el('repairType').value     = r.type;
        el('repairDate').value     = r.date;
        el('repairNextDate').value = r.next_date || '';
        el('repairComment').value  = r.comment || '';
      }
    }
    this._openModal('repairModalBackdrop');
  },

  closeRepairModal() { this._closeModal('repairModalBackdrop'); },

  setNextDate(months) {
    const base = el('repairDate').value ? parseDate(el('repairDate').value) : today();
    const next = new Date(base);
    next.setMonth(next.getMonth() + months);
    el('repairNextDate').value = next.toISOString().slice(0, 10);
  },

  async saveRepair(e) {
    e.preventDefault();
    const data = {
      car_id:    parseInt(el('repairCarId').value),
      type:      el('repairType').value,
      date:      el('repairDate').value,
      next_date: el('repairNextDate').value || null,
      comment:   el('repairComment').value.trim(),
    };
    const id = el('repairId').value ? parseInt(el('repairId').value) : null;
    try {
      if (id) {
        await API.updateRepair(id, data);
      } else {
        await API.createRepair(data);
      }
      window.location.reload();
    } catch {
      Toast.error('Ошибка сохранения');
    }
  },

  confirmDeleteRepair(id) {
    el('confirmText').textContent = 'Удалить запись о ремонте?';
    State.confirmCallback = async () => {
      await API.deleteRepair(id);
      window.location.reload();
    };
    this._openModal('confirmModalBackdrop');
  },

  /* ── DETAIL MODAL ── */
  async openDetailModal(carId) {
    const [car, repairs] = await Promise.all([API.getCar(carId), API.getRepairsForCar(carId)]);
    if (!car) return;

    el('detailModalTitle').textContent = `${car.brand} ${car.model} · ${car.plate}`;
    el('detailModalBody').innerHTML = `
      <div class="detail-grid">
        <div class="detail-field"><div class="detail-field-label">Марка</div><div class="detail-field-value">${car.brand}</div></div>
        <div class="detail-field"><div class="detail-field-label">Модель</div><div class="detail-field-value">${car.model}</div></div>
        <div class="detail-field"><div class="detail-field-label">Гос. номер</div><div class="detail-field-value font-mono">${car.plate}</div></div>
        <div class="detail-field"><div class="detail-field-label">Год выпуска</div><div class="detail-field-value">${car.year}</div></div>
        ${car.note ? `<div class="detail-field" style="grid-column:span 2"><div class="detail-field-label">Примечание</div><div class="detail-field-value">${car.note}</div></div>` : ''}
      </div>
      <div class="detail-section-title">
        История ремонтов
        <button class="btn btn-primary btn-sm" data-car-id="${car.id}" onclick="App.closeDetailModal(); App.openRepairModal(null, +this.dataset.carId)">+ Добавить ремонт</button>
      </div>
      <div class="car-repairs-table"><div class="table-wrap">
        ${repairs.length ? `<table class="data-table">
          <thead><tr><th>Тип</th><th>Дата</th><th>Следующий</th><th>Комментарий</th><th>Действия</th></tr></thead>
          <tbody>${repairs.sort((a,b) => b.date.localeCompare(a.date)).map(r => {
            const st = getRepairStatus(r.next_date);
            return `<tr>
              <td><span class="repair-type">${r.type}</span></td>
              <td>${formatDate(r.date)}</td>
              <td>${r.next_date ? `<span class="status-badge ${st}">${formatDate(r.next_date)}</span>` : '—'}</td>
              <td class="text-muted">${r.comment || '—'}</td>
              <td><div class="table-actions">
                <button class="icon-btn edit" data-id="${r.id}" onclick="App.closeDetailModal(); App.openRepairModal(+this.dataset.id)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <button class="icon-btn del" data-id="${r.id}" onclick="App.closeDetailModal(); App.confirmDeleteRepair(+this.dataset.id)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/></svg>
                </button>
              </div></td>
            </tr>`;
          }).join('')}</tbody>
        </table>` : '<div class="empty-state">Ремонты ещё не добавлены</div>'}
      </div></div>
    `;
    this._openModal('detailModalBackdrop');
  },

  closeDetailModal() { this._closeModal('detailModalBackdrop'); },

  /* ── CONFIRM MODAL ── */
  closeConfirm(confirmed) {
    this._closeModal('confirmModalBackdrop');
    if (confirmed && State.confirmCallback) {
      State.confirmCallback();
      State.confirmCallback = null;
    }
  },

  /* ── Modal helpers ── */
  _openModal(backdropId) {
    el(backdropId).classList.add('open');
    document.body.style.overflow = 'hidden';
  },

  _closeModal(backdropId) {
    el(backdropId).classList.remove('open');
    document.body.style.overflow = '';
  },
};

/* ──────────────────────────────────────────────────────────────
   INIT
   ────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initBadges();

  document.querySelectorAll('.nav-item[data-page]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      App.navigate(link.dataset.page);
    });
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      ['carModalBackdrop', 'repairModalBackdrop', 'detailModalBackdrop', 'confirmModalBackdrop']
        .forEach(id => App._closeModal(id));
    }
  });

  // Set dashboard date
  el('dashDate').textContent = today().toLocaleDateString('ru-RU', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  App.navigate('dashboard');
});
