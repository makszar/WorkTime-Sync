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

export function creatorTag(task) {
  if (task.creator_department) return task.creator_department;
  if (task.creator_role_label === 'HR' || task.created_by_role === 'hr') return 'HR';
  if (task.created_by_role === 'executive') return 'Вся компания';
  return task.creator_name || task.created_by_user_id || 'Автор не указан';
}

export function assigneeTag(task) {
  return task.employee_team || task.department || 'Отдел не указан';
}

export default function TaskCard({ task, user, onStatusChange }) {
  const [comment, setComment] = useState('');
  const [suggestedStart, setSuggestedStart] = useState('');
  const [suggestedEnd, setSuggestedEnd] = useState('');
  const [localError, setLocalError] = useState('');
  const canEmployeeAct = user?.role === 'employee' && ['pending', 'reschedule_requested'].includes(task.status);
  const canClose = ['executive', 'hr', 'department_manager'].includes(user?.role) && task.status !== 'done';
  const creator = useMemo(() => creatorTag(task), [task]);
  const assignee = useMemo(() => assigneeTag(task), [task]);
  const employeeName = task.employee_name || task.employee || `#${task.employee_id}`;

  function submit(status) {
    setLocalError('');

    if (['rejected', 'reschedule_requested'].includes(status) && !comment.trim()) {
      setLocalError('Для отказа или переноса нужен комментарий.');
      return;
    }

    if (status === 'reschedule_requested' && (!suggestedStart.trim() || !suggestedEnd.trim())) {
      setLocalError('Для переноса нужно указать новое начало и новый конец.');
      return;
    }

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

      <div className="taskTagsRow">
        <span className="taskTag authorTag">{creator}</span>
        <span className="taskTag assigneeTag">{assignee}</span>
        <span className="taskTag personTag">{employeeName}</span>
      </div>

      <h3>{task.title}</h3>
      <p>{task.description || task.reason || 'Описание задачи не указано.'}</p>

      <div className="taskMetaGrid compactTaskMeta">
        <span>{employeeName}</span>
        <span>{assignee}</span>
        <span>{task.due_date || '-'}</span>
        <span>{creator}</span>
      </div>

      {task.related_event && (
        <div className="linkedEvent">
          <img src="/icons/calendar.svg" alt="" />
          <span>{eventLabel(task.related_event)}</span>
        </div>
      )}

      {task.employee_comment && <p className="taskComment">Комментарий: {task.employee_comment}</p>}
      {localError && <div className="inlineError">{localError}</div>}

      {(canEmployeeAct || canClose) && (
        <div className="taskActions">
          <textarea
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            placeholder="Комментарий к задаче. Для подтверждения можно оставить пустым. Для отказа или переноса комментарий обязателен."
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
            {canEmployeeAct && task.type === 'reschedule_meeting' && <button className="ghostButton compact" type="button" onClick={() => submit('reschedule_requested')}>Предложить другое время</button>}
            {canClose && <button className="primaryButton small" type="button" onClick={() => submit('done')}>Закрыть</button>}
          </div>
        </div>
      )}
    </article>
  );
}
