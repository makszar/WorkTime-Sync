import { useMemo, useState } from 'react';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';

export default function Tasks({ user, tasks, employees, events, onCreateTask, onTaskStatusChange, onGenerateConflictTasks, onApplyTask }) {
  const [status, setStatus] = useState('');
  const [executorDepartment, setExecutorDepartment] = useState('');
  const [creatorTag, setCreatorTag] = useState('');
  const [showForm, setShowForm] = useState(false);
  const canCreate = ['executive', 'hr', 'department_manager'].includes(user?.role);
  const departments = useMemo(() => [...new Set(tasks.map((task) => task.department || task.employee_team).filter(Boolean))].sort(), [tasks]);
  const creatorTags = useMemo(() => [...new Set(tasks.map((task) => task.creator_tag || task.creator_department || task.creator_role_label || task.created_by_role).filter(Boolean))].sort(), [tasks]);
  const filteredTasks = useMemo(() => tasks.filter((task) => {
    if (status && task.status !== status) return false;
    if (executorDepartment && (task.department || task.employee_team) !== executorDepartment) return false;
    const taskCreatorTag = task.creator_tag || task.creator_department || task.creator_role_label || task.created_by_role;
    if (creatorTag && taskCreatorTag !== creatorTag) return false;
    return true;
  }), [tasks, status, executorDepartment, creatorTag]);

  return (
    <section className="page fadeIn">
      <div className="pageHeader heroHeader">
        <div>
          <span className="eyebrow">Workflow задач</span>
          <h1>{user?.role === 'employee' ? 'Мои задачи и подтверждения' : 'Задачи отдела, HR и встреч'}</h1>
          <p>Задачи создаются через backend, сохраняются в tasks.json, отображаются у исполнителя и подтверждаются сотрудником.</p>
        </div>
        {canCreate && (
          <div className="headerActions">
            <button className="primaryButton big iconTextButton" type="button" onClick={() => setShowForm((value) => !value)}>
              <img src="/icons/edit.svg" alt="" />
              <span>{showForm ? 'Скрыть форму' : 'Создать задачу'}</span>
            </button>
            <button className="ghostButton compact iconTextButton" type="button" onClick={() => onGenerateConflictTasks?.({ task_type: 'meeting_outside_work_approval', limit: 10 })}>
              <img src="/icons/calendar.svg" alt="" />
              <span>Создать по конфликтам</span>
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
            <option value="done">Закрыто</option>
            <option value="expired">Просрочено</option>
            <option value="reschedule_requested">Запрошен перенос</option>
          </select>
        </label>
        <label className="inlineControl">
          <span>Отдел исполнителя</span>
          <select value={executorDepartment} onChange={(event) => setExecutorDepartment(event.target.value)}>
            <option value="">Все</option>
            {departments.map((department) => <option value={department} key={department}>{department}</option>)}
          </select>
        </label>
        <label className="inlineControl">
          <span>Кто создал</span>
          <select value={creatorTag} onChange={(event) => setCreatorTag(event.target.value)}>
            <option value="">Все</option>
            {creatorTags.map((tag) => <option value={tag} key={tag}>{tag}</option>)}
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
          <TaskCard task={task} user={user} onStatusChange={onTaskStatusChange} onApply={onApplyTask} key={task.id} />
        ))}
      </div>
      {!filteredTasks.length && <div className="panel emptyState">Задач по выбранному фильтру нет.</div>}
    </section>
  );
}
