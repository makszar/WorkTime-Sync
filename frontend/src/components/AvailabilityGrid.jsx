import { buildAvailabilityWithEvents } from '../utils/calculations';

function slotTitle(slot) {
  const details = slot.missingDetails || [];
  if (!details.length) return `Доступно: ${slot.count}. Выпадает: никто`;
  return `Доступно: ${slot.count}. Выпадают:\n${details.map((item) => `${item.employee}: ${item.reason}`).join('\n')}`;
}

export default function AvailabilityGrid({ employees = [], events = [], rows = [] }) {
  const computedRows = rows?.length ? rows : buildAvailabilityWithEvents(employees, events);
  const hours = computedRows[0]?.slots.map((slot) => slot.hour) || [];

  return (
    <div className="availabilityWrap">
      <div className="availabilityHeader">
        <span>День</span>
        {hours.map((hour) => <span key={hour}>{hour}:00</span>)}
      </div>

      {computedRows.map((row) => (
        <div className="availabilityRow" key={row.day}>
          <strong>{row.day}</strong>
          {row.slots.map((slot) => (
            <div
              className={`availabilityCell ${slot.type}`}
              title={slotTitle(slot)}
              key={`${row.day}-${slot.hour}`}
            >
              <strong>{slot.count}</strong>
              <small>из {employees.length}</small>
            </div>
          ))}
        </div>
      ))}

      <div className="legend availabilityLegend">
        <span><i className="legendAll" /> доступна вся команда</span>
        <span><i className="legendMajority" /> доступно большинство</span>
        <span><i className="legendWeak" /> слабое окно</span>
      </div>
    </div>
  );
}
