import { useState } from 'react';
import RiskMeter from '../components/RiskMeter';
import ScheduleConfirmationCard from '../components/ScheduleConfirmationCard';
import TaskCard from '../components/TaskCard';
import { actualityScore, loadRate, percent, riskScore } from '../utils/calculations';

function formatEventTime(event) {
  if (event.day || event.time) return [event.day, event.time].filter(Boolean).join(', ');
  if (event.start_datetime && event.end_datetime) {
    const start = new Date(event.start_datetime);
    const end = new Date(event.end_datetime);
    return `${start.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}-${end.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
  }
  return event.start_datetime || 'Время не указано';
}

function mergeEventsWithMeetingTasks(events, meetingTasks) {
  const byId = new Map((events || []).map((event) => [String(event.id), event]));
  (meetingTasks || []).forEach((task) => {
    if (task.related_event?.id !== undefined) byId.set(String(task.related_event.id), task.related_event);
  });
  return [...byId.values()];
}

function extractEmployee(cabinet) {
  return cabinet?.frontend_employee || cabinet?.employee || null;
}

export default function EmployeeCabinet({ cabinet, user, onConfirmSchedule, onTaskStatusChange }) {
  const [comment, setComment] = useState('');
  const employee = extractEmployee(cabinet);
  const tasks = cabinet?.tasks || [];
  const pendingTasks = cabinet?.pendingTasks || tasks.filter((task) => task.status === 'pending');
  const meetingTasks = cabinet?.meetingTasks || tasks.filter((task) => task.type?.includes('meeting'));
  const baseEvents = cabinet?.upcomingEvents || cabinet?.events || [];
  const events = mergeEventsWithMeetingTasks(baseEvents, meetingTasks);

  if (!employee) {
    return <div className="centerState">Личный кабинет сотрудника не найден.</div>;
  }

  const risk = employee.metrics?.risk ?? riskScore(employee);
  const load = employee.metrics?.load ?? loadRate(employee);
  const actuality = employee.metrics?.schedule_actuality ?? actualityScore(employee);

  function confirm() {
    onConfirmSchedule(employee.id, { comment });
  }

  return (
    <section className="page fadeIn">
      <div className="profileHero employeeHero">
        <div>
          <span className="eyebrow">Личный кабинет сотрудника</span>
          <h1>{employee.name}</h1>
          <p>{employee.role} - {employee.team}</p>
        </div>
        <div className="employeeHeroStats">
          <strong>{pendingTasks.length}</strong>
          <span>задач ожидают действия</span>
        </div>
      </div>

      <div className="profileGrid">
        <article className="panel profileInfo">
          <h2>Мой график</h2>
          <dl>
            <div><dt>Рабочие дни</dt><dd>{employee.workDays?.join(', ') || employee.work_days?.join(', ')}</dd></div>
            <div><dt>Рабочее время</dt><dd>{employee.workStart ?? employee.work_start}:00-{employee.workEnd ?? employee.work_end}:00</dd></div>
            <div><dt>Часовой пояс</dt><dd>{employee.timezone}</dd></div>
            <div><dt>Формат</dt><dd>{employee.format || employee.work_format}</dd></div>
          </dl>
        </article>

        <article className="panel">
          <h2>Мои метрики</h2>
          <div className="metricStack">
            <RiskMeter label="Актуальность" value={percent(actuality)} />
            <RiskMeter label="Загрузка" value={percent(load)} />
            <RiskMeter label="Риск" value={percent(risk)} />
          </div>
        </article>
      </div>

      <ScheduleConfirmationCard
        status={cabinet?.scheduleConfirmationStatus || 'not_confirmed'}
        comment={comment}
        canConfirm
        onConfirm={confirm}
      />
      <div className="panel commentPanel">
        <label>
          <span>Комментарий к подтверждению графика</span>
          <textarea value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Например: подтверждаю график или прошу изменить время" />
        </label>
      </div>

      <div className="twoColumns">
        <article className="panel">
          <div className="panelHeader"><h2>Мои события</h2><span>{events.length}</span></div>
          <div className="stackList">
            {events.slice(0, 6).map((event) => (
              <div className="eventItem" key={event.id}>
                <strong>{event.title}</strong>
                <span>{formatEventTime(event)}</span>
                <p>{event.reason || event.type || 'Событие календаря'}</p>
              </div>
            ))}
            {!events.length && <p className="emptyState">Событий нет.</p>}
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader"><h2>Задачи по встречам</h2><span>{meetingTasks.length}</span></div>
          <div className="stackList">
            {meetingTasks.map((task) => <TaskCard task={task} user={user} onStatusChange={onTaskStatusChange} key={task.id} />)}
            {!meetingTasks.length && <p className="emptyState">Задач по встречам нет.</p>}
          </div>
        </article>
      </div>

      <article className="panel">
        <div className="panelHeader"><h2>Мои задачи</h2><span>{tasks.length}</span></div>
        <div className="cardsGrid smallCards">
          {tasks.map((task) => <TaskCard task={task} user={user} onStatusChange={onTaskStatusChange} key={task.id} />)}
        </div>
      </article>
    </section>
  );
}
