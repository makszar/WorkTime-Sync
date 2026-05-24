import { useMemo, useState } from 'react';
import TaskStatusBadge from './TaskStatusBadge';
import TaskTypeBadge from './TaskTypeBadge';

function eventLabel(event) {
  if (!event) return '';
  if (event.start_datetime && event.end_datetime) {
    const start = new Date(event.start_datetime);
    const end = new Date(event.end_datetime);
    return `${event.title || 'Встреча'}: ${start.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}-${end.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
  }
  return event.title || 'Связанная встреча';
}

function getCreatorDepartment(task) {
  return task.created_by_department || task.creator_department || task.creatorDepartment || task.createdByDepartment || task.creator_role_label || task.created_by_role || 'Не указан';
}

function getEmployeeDepartment(task) {
  return task.department || task.employee_team || task.employeeTeam || 'Не указан';
}

function isMeetingTask(task) {
  return task.type?.includes('meeting');
}

export default function TaskCard({ task, user, onStatusChange, onApplyTask }) {
  const [comment, setComment] = useState('');
  const [suggestedStart, setSuggestedStart] = useState(task.suggested_start_datetime || '');
  const [suggestedEnd, setSuggestedEnd] = useState(task.suggested_end_datetime || '');
  const [localError, setLocalError] = useState('');

  const canEmployeeAct = user?.role === 'employee' && task.status === 'pending';
  const canManage = ['executive', 'hr', 'department_manager'].includes(user?.role);
  const canClose = canManage && task.status !== 'done';
  const canApply = canManage && ['confirmed', 'rejected', 'reschedule_requested'].includes(task.status);
  const creatorDepartment = useMemo(() => getCreatorDepartment(task), [task]);
  const employeeDepartment = useMemo(() => getEmployeeDepartment(task), [task]);

  function submit(status) {
    setLocalError('');

    if (['rejected', 'reschedule_requested'].includes(status) && !comment.trim()) {
      setLocalError('Для отклонения или переноса нужен комментарий.');
      return;
    }

    if (status === 'reschedule_requested' && (!suggestedStart || !suggestedEnd)) {
      setLocalError('Для запроса переноса укажите новое начало и конец.');
      return;
    }

    onStatusChange?.(task.id, {
      status,
      employee_comment: comment,
      suggested_start_datetime: suggestedStart || undefined,
      suggested_end_datetime: suggestedEnd || undefined
    });
  }

  function apply() {
    setLocalError('');
    onApplyTask?.(task.id, { action: isMeetingTask(task) ? 'apply_meeting_decision' : 'close_task' });
  }

  return (
    <article className="taskCard">
      <div className="taskCardTop">
        <TaskTypeBadge type={task.type} />
        <TaskStatusBadge status={task.status} />
      </div>

      <div className="taskTagRow">
        <span className="departmentTag creatorTag">Создал: {creatorDepartment}</span>
        <span className="departmentTag executorTag">Исполнитель: {employeeDepartment}</span>
      </div>

      <h3>{task.title}</h3>
      <p>{task.description || task.reason || 'Описание задачи не указано.'}</p>

      <div className="taskMetaGrid">
        <span>Сотрудник: <b>{task.employee_name || task.employee || `#${task.employee_id}`}</b></span>
        <span>Срок: <b>{task.due_date || '-'}</b></span>
        <span>Создал: <b>{task.creator_name || task.created_by_user_id || '-'}</b></span>
        <span>Роль: <b>{task.creator_role_label || task.created_by_role || '-'}</b></span>
      </div>

      {task.related_event && (
        <div className="linkedEvent">
          <img src="/icons/calendar.svg" alt="" />
          <span>{eventLabel(task.related_event)}</span>
        </div>
      )}

      {(task.suggested_start_datetime || task.suggested_end_datetime) && (
        <div className="linkedEvent softWarning">
          <img src="/icons/sort.svg" alt="" />
          <span>Предложенное время: {task.suggested_start_datetime || '-'} - {task.suggested_end_datetime || '-'}</span>
        </div>
      )}

      {task.employee_comment && <p className="taskComment">Комментарий: {task.employee_comment}</p>}
      {localError && <p className="taskLocalError">{localError}</p>}

      {(canEmployeeAct || canClose) && (
        <div className="taskActions">
          {canEmployeeAct && (
            <textarea
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              placeholder="Комментарий к задаче. Для подтверждения можно оставить пустым. Для отказа или переноса комментарий обязателен."
            />
          )}

          {task.type === 'reschedule_meeting' && canEmployeeAct && (
            <div className="formGrid twoInputs">
              <input value={suggestedStart} onChange={(event) => setSuggestedStart(event.target.value)} placeholder="Новое начало: 2026-05-22T12:00:00" />
              <input value={suggestedEnd} onChange={(event) => setSuggestedEnd(event.target.value)} placeholder="Новый конец: 2026-05-22T13:00:00" />
            </div>
          )}

          <div className="actionRow taskActionRow">
            {canEmployeeAct && <button className="primaryButton small" type="button" onClick={() => submit('confirmed')}>Подтвердить</button>}
            {canEmployeeAct && <button className="ghostButton compact" type="button" onClick={() => submit('rejected')}>Отклонить</button>}
            {canEmployeeAct && task.type === 'reschedule_meeting' && <button className="ghostButton compact" type="button" onClick={() => submit('reschedule_requested')}>Запросить перенос</button>}
            {canApply && <button className="primaryButton small" type="button" onClick={apply}>Применить решение</button>}
            {canClose && !canApply && <button className="ghostButton compact" type="button" onClick={() => submit('done')}>Закрыть</button>}
          </div>
        </div>
      )}
    </article>
  );
}
