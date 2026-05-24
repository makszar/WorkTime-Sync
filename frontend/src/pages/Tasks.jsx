import { useMemo, useState } from 'react';
import TaskCard, { assigneeTag, creatorTag } from '../components/TaskCard';
import TaskForm from '../components/TaskForm';

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'ru'));
}

export default function Tasks({ user, tasks, employees, events, onCreateTask, onTaskStatusChange }) {
  const [status, setStatus] = useState('');
  const [assigneeDepartment, setAssigneeDepartment] = useState('');
  const [creatorDepartment, setCreatorDepartment] = useState('');
  const [showForm, setShowForm] = useState(false);
  const canCreate = ['executive', 'hr', 'department_manager'].includes(user?.role);

  const assigneeDepartments = useMemo(() => unique(tasks.map(assigneeTag)), [tasks]);
  const creatorDepartments = useMemo(() => unique(tasks.map(creatorTag)), [tasks]);

  const filteredTasks = useMemo(() => tasks.filter((task) => {
    if (status && task.status !== status) return false;
    if (assigneeDepartment && assigneeTag(task) !== assigneeDepartment) return false;
    if (creatorDepartment && creatorTag(task) !== creatorDepartment) return false;
    return true;
  }), [tasks, status, assigneeDepartment, creatorDepartment]);

  return (
    <section className="page fadeIn tasksPage">
      <div className="pageHeader heroHeader">
        <div>
          <span className="eyebrow">Workflow задач</span>
          <h1>{user?.role === 'employee' ? 'Мои задачи и подтверждения' : 'Задачи отдела, HR и встреч'}</h1>
          <p>Задачи создаются через backend, сохраняются в tasks.json и сразу появляются у исполнителя.</p>
        </div>
        {canCreate && (
          <button className="primaryButton big iconTextButton" type="button" onClick={() => setShowForm((value) => !value)}>
            <img src="/icons/edit.svg" alt="" />
            <span>{showForm ? 'Скрыть форму' : 'Создать задачу'}</span>
          </button>
        )}
      </div>

      <div className="toolbarPanel panel tasksToolbar">
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

        <label className="inlineControl">
          <img src="/icons/companies.svg" alt="" />
          <span>Отдел исполнителя</span>
          <select value={assigneeDepartment} onChange={(event) => setAssigneeDepartment(event.target.value)}>
            <option value="">Все</option>
            {assigneeDepartments.map((department) => <option key={department} value={department}>{department}</option>)}
          </select>
        </label>

        <label className="inlineControl">
          <img src="/icons/work.svg" alt="" />
          <span>Кто создал</span>
          <select value={creatorDepartment} onChange={(event) => setCreatorDepartment(event.target.value)}>
            <option value="">Все</option>
            {creatorDepartments.map((department) => <option key={department} value={department}>{department}</option>)}
          </select>
        </label>

        <strong>{filteredTasks.length} задач</strong>
      </div>

      {showForm && canCreate && (
        <article className="panel taskFormPanel">
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
