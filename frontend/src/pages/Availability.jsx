import AvailabilityGrid from '../components/AvailabilityGrid';

export default function Availability({ employees, slots }) {
  return (
    <section className="page fadeIn">
      <div className="pageHeader">
        <div>
          <span className="eyebrow">Командная карта</span>
          <h1>Когда команда реально доступна</h1>
          <p>Таблица считает доступность по рабочим дням, часам, часовым поясам и загрузке.</p>
        </div>
      </div>

      <div className="panel">
        <AvailabilityGrid employees={employees} />
      </div>

      <div className="cardsGrid smallCards">
        {slots.map((slot) => (
          <article className="slotCard" key={slot.label}>
            <span>Лучший слот</span>
            <h3>{slot.label}</h3>
            <p>Доступно {slot.count} из {employees.length}</p>
            <small>Выпадают: {slot.missing.join(', ') || 'никто'}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
