import { buildAvailability } from '../utils/calculations';

function normalizeAvailabilityRows(rows, employees) {
  if (Array.isArray(rows) && rows.length) return rows;
  return buildAvailability(employees);
}

function slotTitle(slot) {
  const details = slot.missingDetails || [];
  if (details.length) {
    return details.map((item) => `${item.employee}: ${item.reason}`).join('\n');
  }
  return `Доступно: ${slot.count}. Выпадают: ${slot.missing?.join(', ') || 'никто'}`;
}

export default function AvailabilityGrid({ employees, availability }) {
  const rows = normalizeAvailabilityRows(availability, employees);
  const hours = rows[0]?.slots.map((slot) => slot.hour) || [];

  return (
    <div className="availabilityWrap">
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
              title={slotTitle(slot)}
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
