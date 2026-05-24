import AvailabilityGrid from '../components/AvailabilityGrid';
import StatCard from '../components/StatCard';
import { buildAvailabilityWithEvents } from '../utils/calculations';

function flattenRows(rows = []) {
  return rows.flatMap((row) => (row.slots || []).map((slot) => ({ ...slot, day: row.day, label: `${row.day}, ${slot.hour}:00-${slot.hour + 1}:00` })));
}

function availabilityStats(rows = [], employeeCount = 0) {
  const slots = flattenRows(rows);
  const best = [...slots].sort((a, b) => b.count - a.count || a.hour - b.hour)[0];
  return {
    best,
    all: slots.filter((slot) => employeeCount > 0 && slot.count === employeeCount).length,
    majority: slots.filter((slot) => slot.type === 'majority').length,
    weak: slots.filter((slot) => slot.type === 'weak').length
  };
}

export default function Availability({ employees = [], events = [], slots = [], rows = [] }) {
  const availabilityRows = rows?.length ? rows : buildAvailabilityWithEvents(employees, events);
  const stats = availabilityStats(availabilityRows, employees.length);
  const bestSlots = flattenRows(availabilityRows)
    .sort((a, b) => b.count - a.count || a.hour - b.hour)
    .slice(0, 3);
  const displaySlots = bestSlots.length ? bestSlots : slots;

  return (
    <section className="page fadeIn availabilityPage">
      <div className="pageHeader heroHeader availabilityHero">
        <div>
          <span className="eyebrow">Командная карта</span>
          <h1>Когда команда реально доступна</h1>
          <p>Карта берёт расчёт из backend `/analytics/availability`: рабочие часы, календарные события, отсутствия и причины выпадения сотрудников. Если backend недоступен, включается локальный fallback.</p>
        </div>
      </div>

      <div className="statsGrid availabilityStatsGrid">
        <StatCard label="Лучшее окно" value={stats.best ? stats.best.label : '-'} hint={stats.best ? `Доступно ${stats.best.count} из ${employees.length}` : 'Нет данных'} tone="success" />
        <StatCard label="Окна всей команды" value={stats.all} hint="Все сотрудники доступны" tone="success" />
        <StatCard label="Окна большинства" value={stats.majority} hint="Доступно 65%+ команды" tone="warning" />
        <StatCard label="Слабые окна" value={stats.weak} hint="Лучше не назначать встречи" tone="danger" />
      </div>

      <div className="panel availabilityPanel">
        <div className="panelHeader availabilityPanelHeader">
          <div>
            <h2>Почасовая карта доступности</h2>
            <p>Наведите курсор на ячейку, чтобы увидеть, кто именно выпадает и по какой причине.</p>
          </div>
          <span>{employees.length} сотрудников</span>
        </div>
        <AvailabilityGrid employees={employees} events={events} rows={availabilityRows} />
      </div>

      <div className="cardsGrid smallCards availabilitySlotsGrid">
        {displaySlots.map((slot) => (
          <article className="slotCard" key={slot.label}>
            <span>Лучший слот</span>
            <h3>{slot.label}</h3>
            <p>Доступно {slot.count} из {employees.length}</p>
            <small>Выпадают: {slot.missing?.join(', ') || 'никто'}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
