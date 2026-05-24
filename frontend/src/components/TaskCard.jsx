import { useState } from 'react';
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

export default function TaskCard({ task, user, onStatusChange, onApply }) {
  const [comment, setComment] = useState('');
  const [suggestedStart, setSuggestedStart] = useState('');
  const [suggestedEnd, setSuggestedEnd] = useState('');
  const canEmployeeAct = user?.role === 'employee' && task.status === 'pending';
  const canApply = ['executive', 'hr', 'department_manager'].includes(user?.role) && ['confirmed', 'rejected', 'reschedule_requested'].includes(task.status);

  function submit(status) {
    onStatusChange?.(task.id, {
      status,
      employee_comment: comment,
      suggested_start_datetime: suggestedStart || undefined,
      suggested_end_datetime: suggestedEnd || undefined
    });
  }

  return (
    <article className="taskCard">
      <div className="taskCardTop">
        <TaskTypeBadge type={task.type} />
        <TaskStatusBadge status={task.status} />
      </div>
      <h3>{task.title}</h3>
      <p>{task.description || task.reason || 'Описание задачи не указано.'}</p>

      <div className="taskMetaGrid tagGrid">
        <span className="taskTag">{task.creator_tag || task.creator_department || task.creator_role_label || task.created_by_role || '-'}</span>
        <span className="taskTag">{task.employee_team || task.department || '-'}</span>
        <span className="taskTag">{task.employee_name || task.employee || `#${task.employee_id}`}</span>
        <span className="taskTag">до {task.due_date || '-'}</span>
      </div>

      {task.related_event && (
        <div className="linkedEvent">
          <img src="/icons/calendar.svg" alt="" />
          <span>{eventLabel(task.related_event)}</span>
        </div>
      )}

      {task.employee_comment && <p className="taskComment">{task.employee_comment}</p>}

      {(canEmployeeAct || canApply) && (
        <div className="taskActions">
          <textarea
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            placeholder="Комментарий к задаче"
          />
          {task.type === 'reschedule_meeting' && canEmployeeAct && (
            <div className="formGrid twoInputs">
              <input value={suggestedStart} onChange={(event) => setSuggestedStart(event.target.value)} placeholder="Новое начало: 2026-05-22T12:00:00" />
              <input value={suggestedEnd} onChange={(event) => setSuggestedEnd(event.target.value)} placeholder="Новый конец: 2026-05-22T13:00:00" />
            </div>
          )}
          <div className="actionRow">
            {canEmployeeAct && <button className="primaryButton small" type="button" onClick={() => submit('confirmed')}>Подтвердить</button>}
            {canEmployeeAct && <button className="ghostButton compact" type="button" onClick={() => submit('rejected')}>Отклонить</button>}
            {canEmployeeAct && task.type === 'reschedule_meeting' && <button className="ghostButton compact" type="button" onClick={() => submit('reschedule_requested')}>Запросить перенос</button>}
            {canApply && <button className="primaryButton small" type="button" onClick={() => onApply?.(task.id)}>Применить решение</button>}
          </div>
        </div>
      )}
    </article>
  );
}
