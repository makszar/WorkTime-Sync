import { useState } from 'react';
import TaskStatusBadge from './TaskStatusBadge';
import TaskTypeBadge from './TaskTypeBadge';

const APPLY_ROLES = ['executive', 'hr', 'department_manager'];
const MEETING_TYPES = ['meeting_confirmation', 'reschedule_meeting', 'meeting_outside_work_approval'];

function formatDateTime(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function eventLabel(event) {
  if (!event) return '';
  if (event.start_datetime && event.end_datetime) {
    return `${event.title || 'Встреча'}: ${formatDateTime(event.start_datetime)}-${new Date(event.end_datetime).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
  }
  return event.title || 'Связанная встреча';
}

function employeePrimaryAction(task) {
  if (task.type === 'reschedule_meeting') return 'Согласен на перенос';
  if (task.type === 'meeting_confirmation') return 'Подтверждаю участие';
  if (task.type === 'meeting_outside_work_approval') return 'Согласен';
  if (task.type === 'confirm_schedule') return 'Подтверждаю';
  return 'Подтвердить';
}

function employeeRejectAction(task) {
  if (task.type === 'meeting_confirmation') return 'Не могу участвовать';
  if (task.type === 'meeting_outside_work_approval') return 'Не согласен';
  return 'Отклонить';
}

function canRequestReschedule(task) {
  return ['reschedule_meeting', 'meeting_outside_work_approval'].includes(task.type);
}

function canApply(user, task) {
  if (!APPLY_ROLES.includes(user?.role)) return false;
  if (task.status === 'done' || task.status === 'expired' || task.status === 'pending') return false;
  if (task.type === 'reschedule_meeting') return ['confirmed', 'reschedule_requested'].includes(task.status) && task.related_event_id && task.suggested_start_datetime && task.suggested_end_datetime;
  if (task.type === 'meeting_outside_work_approval') return ['confirmed', 'rejected', 'reschedule_requested'].includes(task.status);
  if (task.type === 'meeting_confirmation') return ['confirmed', 'rejected'].includes(task.status);
  return ['confirmed', 'rejected', 'reschedule_requested'].includes(task.status);
}

export default function TaskCard({ task, user, onStatusChange, onApplyTask }) {
  const [comment, setComment] = useState('');
  const [suggestedStart, setSuggestedStart] = useState('');
  const [suggestedEnd, setSuggestedEnd] = useState('');
  const canEmployeeAct = user?.role === 'employee' && ['pending', 'reschedule_requested'].includes(task.status);
  const canManagerClose = APPLY_ROLES.includes(user?.role) && task.status !== 'done';
  const shouldShowRescheduleFields = canEmployeeAct && canRequestReschedule(task);
  const applyAvailable = canApply(user, task);

  function submit(status) {
    onStatusChange?.(task.id, {
      status,
      employee_comment: comment || (status === 'confirmed' ? 'Подтверждаю.' : ''),
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

      <div className="taskMetaGrid">
        <span>Сотрудник: <b>{task.employee_name || task.employee || `#${task.employee_id}`}</b></span>
        <span>Отдел: <b>{task.department || task.employee_team || '-'}</b></span>
        <span>Срок: <b>{task.due_date || '-'}</b></span>
        <span>Создал: <b>{task.creator_name || task.created_by_user_id || '-'}</b></span>
      </div>

      {task.related_event && (
        <div className="linkedEvent">
          <img src="/icons/calendar.svg" alt="" />
          <span>{eventLabel(task.related_event)}</span>
        </div>
      )}

      {(task.suggested_start_datetime || task.suggested_end_datetime) && (
        <div className="suggestedTime">
          <span>Предложенное время</span>
          <strong>{formatDateTime(task.suggested_start_datetime)} - {task.suggested_end_datetime ? new Date(task.suggested_end_datetime).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : ''}</strong>
        </div>
      )}

      {task.employee_comment && <p className="taskComment">Комментарий: {task.employee_comment}</p>}

      {MEETING_TYPES.includes(task.type) && (
        <p className="taskHint">Сотрудник отвечает на задачу, а финальное изменение встречи применяет руководитель, HR или полный руководитель.</p>
      )}

      {(canEmployeeAct || canManagerClose || applyAvailable) && (
        <div className="taskActions">
          {canEmployeeAct && (
            <textarea
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              placeholder="Комментарий к задаче. Для отказа или переноса комментарий обязателен"
            />
          )}
          {shouldShowRescheduleFields && (
            <div className="formGrid twoInputs">
              <input value={suggestedStart} onChange={(event) => setSuggestedStart(event.target.value)} placeholder="Новое начало: 2026-05-22T12:00:00" />
              <input value={suggestedEnd} onChange={(event) => setSuggestedEnd(event.target.value)} placeholder="Новый конец: 2026-05-22T13:00:00" />
            </div>
          )}
          <div className="actionRow">
            {canEmployeeAct && <button className="primaryButton small" type="button" onClick={() => submit('confirmed')}>{employeePrimaryAction(task)}</button>}
            {canEmployeeAct && canRequestReschedule(task) && <button className="ghostButton compact" type="button" onClick={() => submit('reschedule_requested')}>Предложить другое время</button>}
            {canEmployeeAct && <button className="ghostButton compact" type="button" onClick={() => submit('rejected')}>{employeeRejectAction(task)}</button>}
            {applyAvailable && <button className="primaryButton small" type="button" onClick={() => onApplyTask?.(task.id, { action: 'apply_reschedule' })}>Применить решение</button>}
            {canManagerClose && !applyAvailable && task.status !== 'pending' && <button className="ghostButton compact" type="button" onClick={() => submit('done')}>Закрыть без применения</button>}
          </div>
        </div>
      )}
    </article>
  );
}
