import StatCard from '../components/StatCard';
import RecommendationCard from '../components/RecommendationCard';

export default function Dashboard({ data, setPage }) {
  return (
    <section className="page fadeIn">
      <div className="pageHeader heroHeader">
        <div>
          <span className="eyebrow">Командная диагностика</span>
          <h1>Показываем, у кого устарел график, где конфликт и что делать дальше</h1>
          <p>На экране руководителя отображается его отдел. В общей базе демо лежит {data.totalSyntheticEmployees || data.summary.total} синтетических сотрудников.</p>
        </div>
        <button className="primaryButton big iconTextButton" type="button" onClick={() => setPage('recommendations')}>
          <img src="/icons/notifications.svg" alt="" />
          <span>Смотреть действия</span>
        </button>
      </div>

      <div className="statsGrid">
        <StatCard label="Сотрудников" value={data.summary.total} hint="В вашем отделе" />
        <StatCard label="Актуальные графики" value={data.summary.current} hint="Подтверждены и без риска" tone="success" />
        <StatCard label="Устаревшие" value={data.summary.outdated} hint="Больше 90 дней без обновления" tone="warning" />
        <StatCard label="Высокий риск" value={data.summary.highRisk} hint="Нужно проверить первым" tone="danger" />
        <StatCard label="Конфликты" value={data.summary.conflicts} hint="Встречи вне рабочего времени" tone="warning" />
        <StatCard label="Средняя загрузка" value={`${data.summary.averageLoad}%`} hint="По встречам и задачам" />
      </div>

      <div className="twoColumns">
        <article className="panel">
          <div className="panelHeader">
            <h2>Лучшие слоты для встречи</h2>
            <span>2-3 варианта</span>
          </div>
          <div className="slotList">
            {data.bestSlots.map((slot) => (
              <div className="slotItem" key={slot.label}>
                <strong>{slot.label}</strong>
                <span>Доступно {slot.count} из {data.summary.total}</span>
                <p>Выпадают: {slot.missing.join(', ') || 'никто'}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <h2>Главные рекомендации</h2>
            <span>по приоритету</span>
          </div>
          <div className="recommendationsCompact">
            {data.recommendations.slice(0, 3).map((item) => (
              <RecommendationCard item={item} key={`${item.title}-${item.reason}`} />
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}
