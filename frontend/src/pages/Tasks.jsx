import { useMemo, useState } from 'react';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';

export default function Tasks({ user, tasks, employees, events, onCreateTask, onTaskStatusChange }) {
  const [status, setStatus] = useState('');
  const [showForm, setShowForm] = useState(false);
  const canCreate = ['executive', 'hr', 'department_manager'].includes(user?.role);
  const filteredTasks = useMemo(() => status ? tasks.filter((task) => task.status === status) : tasks, [tasks, status]);

  return (
    <section className="page fadeIn">
      <div className="pageHeader heroHeader">
        <div>
          <span className="eyebrow">Workflow задач</span>
          <h1>{user?.role === 'employee' ? 'Мои задачи и подтверждения' : 'Задачи отдела, HR и встреч'}</h1>
          <p>Интерфейс подключён к /tasks, /tasks/my, созданию задач и изменению статусов.</p>
        </div>
        {canCreate && (
          <button className="primaryButton big iconTextButton" type="button" onClick={() => setShowForm((value) => !value)}>
            <img src="/icons/edit.svg" alt="" />
            <span>{showForm ? 'Скрыть форму' : 'Создать задачу'}</span>
          </button>
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
            <option value="done">Закрыто</option>
            <option value="expired">Просрочено</option>
            <option value="reschedule_requested">Запрошен перенос</option>
          </select>
        </label>
        <strong>{filteredTasks.length} задач</strong>
      </div>

      {showForm && canCreate && (
        <article className="panel">
          <div className="panelHeader"><h2>Новая задача</h2><span>сотруднику или по встрече</span></div>
          <TaskForm employees={employees} events={events} onCreate={onCreateTask} />
        </article>
      )}

      <div className="cardsGrid taskCardsGrid">
        {filteredTasks.map((task) => (
          <TaskCard task={task} user={user} onStatusChange={onTaskStatusChange} key={task.id} />
        ))}
      </div>
      {!filteredTasks.length && <div className="panel emptyState">Задач по выбранному фильтру нет.</div>}
    </section>
  );
}
