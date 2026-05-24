import AvailabilityGrid from '../components/AvailabilityGrid';
import { buildAvailability } from '../utils/calculations';

function flattenSlots(rows) {
  return rows.flatMap((row) => row.slots.map((slot) => ({ ...slot, day: row.day, label: `${row.day}, ${slot.hour}:00-${slot.hour + 1}:00` })));
}

export default function Availability({ employees, slots = [], availability }) {
  const rows = availability?.length ? availability : buildAvailability(employees);
  const flat = flattenSlots(rows);
  const allCount = flat.filter((slot) => slot.type === 'all').length;
  const majorityCount = flat.filter((slot) => slot.type === 'majority').length;
  const weakCount = flat.filter((slot) => slot.type === 'weak').length;
  const best = [...flat].sort((a, b) => b.count - a.count || a.hour - b.hour)[0];
  const bestSlots = flat.length ? [...flat].sort((a, b) => b.count - a.count || a.hour - b.hour).slice(0, 3) : slots;

  return (
    <section className="page fadeIn availabilityPage">
      <div className="pageHeader heroHeader availabilityHero">
        <div>
          <span className="eyebrow">Командная карта</span>
          <h1>Когда команда реально доступна</h1>
          <p>Карта берёт расчёт backend: рабочие часы, календарные события, отсутствия и причины выпадения сотрудников.</p>
        </div>
      </div>

      <div className="availabilityStats">
        <article className="statCard"><span>Лучшее окно</span><strong>{best?.label || '-'}</strong><p>Доступно {best?.count ?? 0} из {employees.length}</p></article>
        <article className="statCard success"><span>Окна всей команды</span><strong>{allCount}</strong><p>Все сотрудники доступны</p></article>
        <article className="statCard warning"><span>Окна большинства</span><strong>{majorityCount}</strong><p>Доступно 65%+ команды</p></article>
        <article className="statCard"><span>Слабые окна</span><strong>{weakCount}</strong><p>Лучше не назначать встречи</p></article>
      </div>

      <div className="panel availabilityPanel">
        <div className="panelHeader"><h2>Почасовая карта доступности</h2><span>{employees.length} сотрудников</span></div>
        <AvailabilityGrid employees={employees} availability={rows} />
      </div>

      <div className="cardsGrid smallCards availabilityBestSlots">
        {bestSlots.map((slot) => (
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
