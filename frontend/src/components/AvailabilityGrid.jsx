import { buildAvailability } from '../utils/calculations';

function normalizeRows(rows, employees) {
  if (rows?.length) return rows;
  return buildAvailability(employees);
}

function tooltip(slot) {
  const details = slot.missingDetails || [];
  if (details.length) {
    return `Доступно: ${slot.count}. Выпадают: ${details.map((item) => `${item.employee}: ${item.reason}`).join('; ')}`;
  }
  return `Доступно: ${slot.count}. Выпадают: ${slot.missing?.join(', ') || 'никто'}`;
}

export default function AvailabilityGrid({ employees, rows: realRows }) {
  const rows = normalizeRows(realRows, employees);
  const hours = rows[0]?.slots.map((slot) => slot.hour) || [];

  return (
    <div className="availabilityWrap realAvailabilityWrap">
      <div className="availabilityHeader">
        <span>День</span>
        {hours.map((hour) => <span key={hour}>{hour}:00</span>)}
      </div>

      {rows.map((row) => (
        <div className="availabilityRow" key={row.day}>
          <strong>{row.day}</strong>
          {row.slots.map((slot) => (
            <div
              className={`availabilityCell ${slot.type}`}
              title={tooltip(slot)}
              key={`${row.day}-${slot.hour}`}
            >
              {slot.count}
            </div>
          ))}
        </div>
      ))}

      <div className="legend">
        <span><i className="legendAll" /> доступна вся команда</span>
        <span><i className="legendMajority" /> доступно большинство</span>
        <span><i className="legendWeak" /> слабое окно</span>
      </div>
    </div>
  );
}
