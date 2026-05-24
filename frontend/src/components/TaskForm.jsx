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

export default function TaskForm({ employees, events = [], onCreate }) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [meta, setMeta] = useState(null);
  const selectedType = useMemo(() => meta?.taskTypes?.find((item) => item.value === form.type), [meta, form.type]);
  const employeeEvents = events.filter((event) => Number(event.employeeId ?? event.employee_id) === Number(form.employee_id));

  useEffect(() => {
    loadTasksMeta().then(setMeta).catch(() => setMeta(null));
  }, []);

  useEffect(() => {
    const action = MEETING_ACTION_BY_TYPE[form.type] || '';
    setForm((current) => ({ ...current, meeting_action: action, related_event_id: action ? current.related_event_id : '' }));
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
            {(meta?.taskTypes || [
              { value: 'confirm_schedule', label: 'Подтвердить график' },
              { value: 'review_hr_profile', label: 'Проверить HR-профиль' },
              { value: 'review_load', label: 'Проверить нагрузку' },
              { value: 'meeting_confirmation', label: 'Подтвердить встречу' },
              { value: 'reschedule_meeting', label: 'Перенести встречу' },
              { value: 'meeting_outside_work_approval', label: 'Согласовать встречу вне времени' }
            ]).map((type) => <option value={type.value} key={type.value}>{type.label}</option>)}
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
              {employeeEvents.map((event) => <option value={event.id} key={event.id}>{event.title} - {event.day || ''} {event.time || ''}</option>)}
            </select>
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
