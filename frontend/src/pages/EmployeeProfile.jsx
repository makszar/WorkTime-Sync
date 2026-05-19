import RiskMeter from '../components/RiskMeter';
import StatusBadge from '../components/StatusBadge';
import { actualityScore, conflictRate, daysSince, loadRate, percent, riskLevel, riskScore } from '../utils/calculations';

export default function EmployeeProfile({ employee, events, recommendations, goBack }) {
  const level = riskLevel(employee);
  const employeeEvents = events.filter((event) => event.employeeId === employee.id);
  const personalRecommendations = recommendations.filter((item) => item.title.includes(employee.name) || item.reason.includes(employee.name));

  return (
    <section className="page fadeIn">
      <button className="ghostButton" type="button" onClick={goBack}>Назад к сотрудникам</button>

      <div className="profileHero">
        <div>
          <span className="eyebrow">Карточка сотрудника</span>
          <h1>{employee.name}</h1>
          <p>{employee.role} - {employee.team}</p>
        </div>
        <StatusBadge label={level.label} tone={level.tone} />
      </div>

      <div className="profileGrid">
        <article className="panel profileInfo">
          <h2>Профиль рабочего времени</h2>
          <dl>
            <div><dt>Рабочие дни</dt><dd>{employee.workDays.join(', ')}</dd></div>
            <div><dt>Рабочее время</dt><dd>{employee.workStart}:00-{employee.workEnd}:00</dd></div>
            <div><dt>Часовой пояс</dt><dd>{employee.timezone}</dd></div>
            <div><dt>Формат</dt><dd>{employee.format}</dd></div>
            <div><dt>Последнее обновление</dt><dd>{employee.updatedAt} - {daysSince(employee.updatedAt)} дней назад</dd></div>
          </dl>
          <p className="noteText">{employee.statusNote}</p>
        </article>

        <article className="panel">
          <h2>Показатели</h2>
          <div className="metricStack">
            <RiskMeter label="Актуальность" value={percent(actualityScore(employee))} />
            <RiskMeter label="Встречи вне времени" value={percent(conflictRate(employee))} />
            <RiskMeter label="Загрузка" value={percent(loadRate(employee))} />
            <RiskMeter label="Интегральный риск" value={percent(riskScore(employee))} />
          </div>
        </article>
      </div>

      <div className="twoColumns">
        <article className="panel">
          <div className="panelHeader">
            <h2>Конфликтные события</h2>
            <span>{employeeEvents.length}</span>
          </div>
          {employeeEvents.length ? employeeEvents.map((event) => (
            <div className="eventItem" key={event.id}>
              <strong>{event.title}</strong>
              <span>{event.day}, {event.time}</span>
              <p>{event.reason}</p>
            </div>
          )) : <p className="emptyState">Конфликтов нет.</p>}
        </article>

        <article className="panel">
          <div className="panelHeader">
            <h2>Персональные рекомендации</h2>
            <span>{personalRecommendations.length}</span>
          </div>
          {personalRecommendations.length ? personalRecommendations.map((item) => (
            <div className="eventItem" key={`${item.title}-${item.reason}`}>
              <strong>{item.title}</strong>
              <span>{item.priority}</span>
              <p>{item.reason}</p>
            </div>
          )) : <p className="emptyState">Специальных действий нет.</p>}
        </article>
      </div>
    </section>
  );
}
