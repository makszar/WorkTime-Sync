import { useEffect, useMemo, useState } from 'react';
import { loadTasksMeta, MEETING_ACTION_BY_TYPE } from '../api/worktimeApi';

const DEFAULT_FORM = {
  employee_id: '',
  type: 'confirm_schedule',
  title: '',
  description: '',
  due_date: '2026-05-25',
  related_event_id: '',
  meeting_action: '',
  suggested_start_datetime: '',
  suggested_end_datetime: ''
};

const FALLBACK_META = {
  taskTypes: [
    { value: 'confirm_schedule', label: 'Подтвердить график', requiresRelatedEvent: false, requiresSuggestedRange: false },
    { value: 'review_hr_profile', label: 'Проверить HR-профиль', requiresRelatedEvent: false, requiresSuggestedRange: false },
    { value: 'review_load', label: 'Проверить нагрузку', requiresRelatedEvent: false, requiresSuggestedRange: false },
    { value: 'update_timezone', label: 'Проверить часовой пояс', requiresRelatedEvent: false, requiresSuggestedRange: false },
    { value: 'meeting_confirmation', label: 'Подтвердить встречу', requiresRelatedEvent: true, requiresSuggestedRange: false },
    { value: 'reschedule_meeting', label: 'Перенести встречу', requiresRelatedEvent: true, requiresSuggestedRange: true },
    { value: 'meeting_outside_work_approval', label: 'Согласовать встречу вне времени', requiresRelatedEvent: true, requiresSuggestedRange: false }
  ]
};

function eventTitle(event) {
  const start = event.start_datetime ? new Date(event.start_datetime) : null;
  const end = event.end_datetime ? new Date(event.end_datetime) : null;
  if (start && end && !Number.isNaN(start.getTime())) {
    return `${event.title} - ${start.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}-${end.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`;
  }
  return `${event.title} - ${event.day || ''} ${event.time || ''}`.trim();
}

export default function TaskForm({ employees, events = [], onCreate, currentUser }) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [meta, setMeta] = useState(FALLBACK_META);
  const taskTypes = meta?.taskTypes?.length ? meta.taskTypes : FALLBACK_META.taskTypes;
  const selectedType = useMemo(() => taskTypes.find((item) => item.value === form.type), [taskTypes, form.type]);
  const employeeEvents = events.filter((event) => Number(event.employeeId ?? event.employee_id) === Number(form.employee_id));

  useEffect(() => {
    loadTasksMeta().then((payload) => setMeta(payload || FALLBACK_META)).catch(() => setMeta(FALLBACK_META));
  }, []);

  useEffect(() => {
    const action = MEETING_ACTION_BY_TYPE[form.type] || '';
    setForm((current) => ({
      ...current,
      meeting_action: action,
      related_event_id: action ? current.related_event_id : '',
      suggested_start_datetime: form.type === 'reschedule_meeting' ? current.suggested_start_datetime : '',
      suggested_end_datetime: form.type === 'reschedule_meeting' ? current.suggested_end_datetime : ''
    }));
  }, [form.type]);

  function setValue(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function submit(event) {
    event.preventDefault();
    const payload = {
      employee_id: Number(form.employee_id),
      type: form.type,
      title: form.title || selectedType?.label || 'Новая задача',
      description: form.description || 'Задача создана из интерфейса WorkTime-Sync.',
      due_date: form.due_date,
      related_event_id: form.related_event_id ? Number(form.related_event_id) : null,
      meeting_action: form.meeting_action || null,
      suggested_start_datetime: form.suggested_start_datetime || null,
      suggested_end_datetime: form.suggested_end_datetime || null
    };
    onCreate(payload);
    setForm(DEFAULT_FORM);
  }

  return (
    <form className="taskForm" onSubmit={submit}>
      <div className="creatorHint">
        Задачу создаёт: <b>{currentUser?.department || currentUser?.role_label || currentUser?.role || 'текущий пользователь'}</b>
      </div>

      <div className="formGrid">
        <label>
          <span>Сотрудник</span>
          <select value={form.employee_id} onChange={(event) => setValue('employee_id', event.target.value)} required>
            <option value="">Выберите сотрудника</option>
            {employees.map((employee) => <option value={employee.id} key={employee.id}>{employee.name} - {employee.team}</option>)}
          </select>
        </label>
        <label>
          <span>Тип задачи</span>
          <select value={form.type} onChange={(event) => setValue('type', event.target.value)}>
            {taskTypes.map((type) => <option value={type.value} key={type.value}>{type.label}</option>)}
          </select>
        </label>
      </div>

      <label>
        <span>Название</span>
        <input value={form.title} onChange={(event) => setValue('title', event.target.value)} placeholder="Например: подтвердить график" />
      </label>
      <label>
        <span>Описание</span>
        <textarea value={form.description} onChange={(event) => setValue('description', event.target.value)} placeholder="Что нужно сделать сотруднику" />
      </label>

      <div className="formGrid">
        <label>
          <span>Срок</span>
          <input type="date" value={form.due_date} onChange={(event) => setValue('due_date', event.target.value)} required />
        </label>
        {selectedType?.requiresRelatedEvent && (
          <label>
            <span>Связанная встреча</span>
            <select value={form.related_event_id} onChange={(event) => setValue('related_event_id', event.target.value)} required>
              <option value="">Выберите встречу</option>
              {employeeEvents.map((item) => <option value={item.id} key={item.id}>{eventTitle(item)}</option>)}
            </select>
            {!employeeEvents.length && <small className="fieldHint">Для выбранного сотрудника в текущей выборке нет конфликтных встреч.</small>}
          </label>
        )}
      </div>

      {selectedType?.requiresSuggestedRange && (
        <div className="formGrid">
          <label><span>Новое начало</span><input value={form.suggested_start_datetime} onChange={(event) => setValue('suggested_start_datetime', event.target.value)} placeholder="2026-05-22T12:00:00" required /></label>
          <label><span>Новый конец</span><input value={form.suggested_end_datetime} onChange={(event) => setValue('suggested_end_datetime', event.target.value)} placeholder="2026-05-22T13:00:00" required /></label>
        </div>
      )}

      <button className="primaryButton iconTextButton" type="submit">
        <img src="/icons/save.svg" alt="" />
        <span>Создать задачу</span>
      </button>
    </form>
  );
}
