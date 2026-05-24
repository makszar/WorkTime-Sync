import { useMemo } from 'react';
import AvailabilityGrid from '../components/AvailabilityGrid';
import { buildAvailability } from '../utils/calculations';

function flattenSlots(rows = []) {
  return rows.flatMap((row) => row.slots.map((slot) => ({ ...slot, day: row.day })));
}

export default function Availability({ employees, slots = [], availabilityRows, events = [] }) {
  const rows = useMemo(() => availabilityRows?.length ? availabilityRows : buildAvailability(employees, events), [availabilityRows, employees, events]);
  const flat = useMemo(() => flattenSlots(rows), [rows]);
  const fullTeamSlots = flat.filter((slot) => slot.type === 'all').length;
  const majoritySlots = flat.filter((slot) => slot.type === 'majority').length;
  const weakSlots = flat.filter((slot) => slot.type === 'weak').length;
  const best = [...flat].sort((a, b) => b.count - a.count || a.hour - b.hour)[0];

  return (
    <section className="page fadeIn availabilityPage">
      <div className="pageHeader heroHeader availabilityHero">
        <div>
          <span className="eyebrow">Командная карта</span>
          <h1>Когда команда реально доступна</h1>
          <p>Карта берёт расчёт из backend `/analytics/availability`: учитываются рабочие часы, встречи, отсутствия и причины выпадения.</p>
        </div>
      </div>

      <div className="cardsGrid smallCards availabilityStats">
        <article className="slotCard">
          <span>Лучшее окно</span>
          <h3>{best ? `${best.day}, ${best.hour}:00-${best.hour + 1}:00` : '-'}</h3>
          <p>Доступно {best?.count ?? 0} из {employees.length}</p>
        </article>
        <article className="slotCard">
          <span>Вся команда</span>
          <h3>{fullTeamSlots}</h3>
          <p>окон без выпавших сотрудников</p>
        </article>
        <article className="slotCard">
          <span>Большинство</span>
          <h3>{majoritySlots}</h3>
          <p>окон, где доступна большая часть</p>
        </article>
        <article className="slotCard">
          <span>Слабые окна</span>
          <h3>{weakSlots}</h3>
          <p>лучше не использовать для общих встреч</p>
        </article>
      </div>

      <div className="panel availabilityPanel">
        <AvailabilityGrid employees={employees} rows={rows} />
      </div>

      <div className="cardsGrid smallCards bestSlotCards">
        {slots.map((slot) => (
          <article className="slotCard" key={slot.label}>
            <span>Рекомендованный слот</span>
            <h3>{slot.label}</h3>
            <p>Доступно {slot.count} из {employees.length}</p>
            <small>Выпадают: {slot.missing?.join(', ') || 'никто'}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
