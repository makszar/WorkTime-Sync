import { useMemo, useState } from 'react';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';

const STATUS_OPTIONS = [
  ['', 'Все'],
  ['pending', 'Ожидает действия'],
  ['confirmed', 'Подтверждено'],
  ['rejected', 'Отклонено'],
  ['done', 'Закрыто'],
  ['expired', 'Просрочено'],
  ['reschedule_requested', 'Запрошен перенос']
];

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'ru'));
}

function creatorDepartment(task) {
  return task.created_by_department || task.creator_department || task.creatorDepartment || task.createdByDepartment || task.creator_role_label || task.created_by_role || 'Не указан';
}

function taskDepartment(task) {
  return task.department || task.employee_team || task.employeeTeam || 'Не указан';
}

export default function Tasks({
  user,
  tasks = [],
  employees = [],
  events = [],
  departments = [],
  onCreateTask,
  onTaskStatusChange,
  onApplyTask,
  onGenerateConflictTasks
}) {
  const [status, setStatus] = useState('');
  const [department, setDepartment] = useState('');
  const [createdByDepartment, setCreatedByDepartment] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [generationType, setGenerationType] = useState('meeting_outside_work_approval');
  const canCreate = ['executive', 'hr', 'department_manager'].includes(user?.role);

  const departmentOptions = useMemo(() => unique([
    ...departments.map((item) => item.name || item.department),
    ...employees.map((employee) => employee.team),
    ...tasks.map(taskDepartment)
  ]), [departments, employees, tasks]);

  const creatorDepartmentOptions = useMemo(() => unique(tasks.map(creatorDepartment)), [tasks]);

  const filteredTasks = useMemo(() => tasks.filter((task) => {
    if (status && task.status !== status) return false;
    if (department && taskDepartment(task) !== department) return false;
    if (createdByDepartment && creatorDepartment(task) !== createdByDepartment) return false;
    return true;
  }), [tasks, status, department, createdByDepartment]);

  function generateTasks() {
    onGenerateConflictTasks?.({ task_type: generationType, limit: 10 });
  }

  return (
    <section className="page fadeIn tasksPage">
      <div className="pageHeader heroHeader tasksHero">
        <div>
          <span className="eyebrow">Workflow задач</span>
          <h1>{user?.role === 'employee' ? 'Мои задачи и подтверждения' : 'Задачи отдела, HR и встреч'}</h1>
          <p>
            Задачи создаются через backend, сохраняются в <b>tasks.json</b>, сразу появляются в списке и могут быть подтверждены сотрудником.
          </p>
        </div>
        {canCreate && (
          <div className="taskHeroActions">
            <button className="primaryButton big iconTextButton" type="button" onClick={() => setShowForm((value) => !value)}>
              <img src="/icons/edit.svg" alt="" />
              <span>{showForm ? 'Скрыть форму' : 'Создать задачу'}</span>
            </button>
          </div>
        )}
      </div>

      <div className="toolbarPanel panel taskToolbar">
        <label className="inlineControl">
          <img src="/icons/filter.svg" alt="" />
          <span>Статус</span>
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            {STATUS_OPTIONS.map(([value, label]) => <option value={value} key={value || 'all'}>{label}</option>)}
          </select>
        </label>
        <label className="inlineControl">
          <span>Отдел исполнителя</span>
          <select value={department} onChange={(event) => setDepartment(event.target.value)}>
            <option value="">Все</option>
            {departmentOptions.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>
        <label className="inlineControl">
          <span>Кто создал</span>
          <select value={createdByDepartment} onChange={(event) => setCreatedByDepartment(event.target.value)}>
            <option value="">Все</option>
            {creatorDepartmentOptions.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>
        <strong>{filteredTasks.length} задач</strong>
      </div>

      {canCreate && (
        <div className="panel generationPanel">
          <div>
            <h2>Быстро создать задачи по конфликтным встречам</h2>
            <p>Backend найдёт встречи вне рабочего времени в доступном отделе и создаст задачи без дублей.</p>
          </div>
          <label className="inlineControl generationSelect">
            <span>Тип</span>
            <select value={generationType} onChange={(event) => setGenerationType(event.target.value)}>
              <option value="meeting_outside_work_approval">Согласовать встречу вне рабочего времени</option>
              <option value="reschedule_meeting">Согласовать перенос встречи</option>
            </select>
          </label>
          <button className="ghostButton compact iconTextButton" type="button" onClick={generateTasks}>
            <img src="/icons/calendar.svg" alt="" />
            <span>Создать по конфликтам</span>
          </button>
        </div>
      )}

      {showForm && canCreate && (
        <article className="panel taskFormPanel">
          <div className="panelHeader"><h2>Новая задача</h2><span>сотруднику или по встрече</span></div>
          <TaskForm employees={employees} events={events} onCreate={onCreateTask} currentUser={user} />
        </article>
      )}

      <div className="cardsGrid taskCardsGrid">
        {filteredTasks.map((task) => (
          <TaskCard
            task={task}
            user={user}
            onStatusChange={onTaskStatusChange}
            onApplyTask={onApplyTask}
            key={task.id}
          />
        ))}
      </div>
      {!filteredTasks.length && <div className="panel emptyState">Задач по выбранному фильтру нет.</div>}
    </section>
  );
}
