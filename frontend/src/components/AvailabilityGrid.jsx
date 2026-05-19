import { buildAvailability } from '../utils/calculations';

export default function AvailabilityGrid({ employees }) {
  const rows = buildAvailability(employees);
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
              title={`Доступно: ${slot.count}. Выпадают: ${slot.missing.join(', ') || 'никто'}`}
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
