import StatusBadge from '../components/StatusBadge';

export default function Conflicts({ events }) {
  return (
    <section className="page fadeIn">
      <div className="pageHeader">
        <div>
          <span className="eyebrow">Конфликты</span>
          <h1>События вне рабочего времени</h1>
          <p>Экран показывает, какие встречи нарушают заявленный график и почему это важно.</p>
        </div>
      </div>

      <div className="panel">
        <div className="conflictList">
          {events.map((event) => (
            <article className="conflictItem" key={event.id}>
              <div>
                <span className="eyebrow">{event.employee}</span>
                <h3>{event.title}</h3>
                <p>{event.reason}</p>
              </div>
              <div className="conflictSide">
                <strong>{event.day}, {event.time}</strong>
                <StatusBadge label={event.severity} tone={event.severity === 'Высокая' ? 'high' : 'medium'} />
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
