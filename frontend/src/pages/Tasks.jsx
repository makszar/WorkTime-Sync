import { useMemo, useState } from 'react';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';

export default function Tasks({ user, tasks, employees, events, onCreateTask, onTaskStatusChange, onApplyTask, onGenerateConflictTasks }) {
  const [status, setStatus] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [generateType, setGenerateType] = useState('meeting_outside_work_approval');
  const canCreate = ['executive', 'hr', 'department_manager'].includes(user?.role);
  const filteredTasks = useMemo(() => status ? tasks.filter((task) => task.status === status) : tasks, [tasks, status]);

  return (
    <section className="page fadeIn tasksPage">
      <div className="pageHeader heroHeader tasksHero">
        <div>
          <span className="eyebrow">Workflow задач</span>
          <h1>{user?.role === 'employee' ? 'Мои задачи и подтверждения' : 'Задачи отдела, HR и встреч'}</h1>
          <p>Интерфейс подключён к `/tasks`, `/tasks/my`, созданию задач, ответам сотрудников и применению решений через `/tasks/:id/apply`.</p>
        </div>
        {canCreate && (
          <div className="headerActions">
            <button className="primaryButton big iconTextButton" type="button" onClick={() => setShowForm((value) => !value)}>
              <img src="/icons/edit.svg" alt="" />
              <span>{showForm ? 'Скрыть форму' : 'Создать задачу'}</span>
            </button>
          </div>
        )}
      </div>

      <div className="toolbarPanel panel">
        <label className="inlineControl">
          <img src="/icons/filter.svg" alt="" />
          <span>Статус</span>
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">Все</option>
            <option value="pending">Ожидает действия</option>
            <option value="confirmed">Подтверждено</option>
            <option value="rejected">Отклонено</option>
            <option value="reschedule_requested">Запрошен перенос</option>
            <option value="done">Закрыто</option>
            <option value="expired">Просрочено</option>
          </select>
        </label>
        <strong>{filteredTasks.length} задач</strong>
      </div>

      {canCreate && (
        <div className="panel generatorPanel">
          <div>
            <h2>Автозадачи по конфликтным встречам</h2>
            <p>Backend найдёт встречи вне рабочего времени в доступном scope и создаст задачи, если открытой задачи по встрече ещё нет.</p>
          </div>
          <div className="generatorControls">
            <select value={generateType} onChange={(event) => setGenerateType(event.target.value)}>
              <option value="meeting_outside_work_approval">Согласовать вне рабочего времени</option>
              <option value="reschedule_meeting">Предложить перенос встречи</option>
            </select>
            <button className="ghostButton compact iconTextButton" type="button" onClick={() => onGenerateConflictTasks?.({ task_type: generateType })}>
              <img src="/icons/notifications.svg" alt="" />
              <span>Сгенерировать</span>
            </button>
          </div>
        </div>
      )}

      {showForm && canCreate && (
        <article className="panel">
          <div className="panelHeader"><h2>Новая задача</h2><span>сотруднику или по встрече</span></div>
          <TaskForm employees={employees} events={events} onCreate={onCreateTask} />
        </article>
      )}

      <div className="cardsGrid taskCardsGrid">
        {filteredTasks.map((task) => (
          <TaskCard task={task} user={user} onStatusChange={onTaskStatusChange} onApplyTask={onApplyTask} key={task.id} />
        ))}
      </div>
      {!filteredTasks.length && <div className="panel emptyState">Задач по выбранному фильтру нет.</div>}
    </section>
  );
}
