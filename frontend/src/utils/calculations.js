const MAX_DAYS_WITHOUT_UPDATE = 90;
const DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'];
const HOURS = Array.from({ length: 13 }, (_, index) => index + 8);

export function clamp(value, min = 0, max = 1) {
  return Math.min(Math.max(Number.isFinite(value) ? value : 0, min), max);
}

export function daysSince(dateString) {
  if (!dateString) return 0;
  const today = new Date('2026-05-19T12:00:00');
  const target = new Date(`${dateString}T12:00:00`);
  const diff = today.getTime() - target.getTime();
  return Math.max(0, Math.round(diff / (1000 * 60 * 60 * 24)));
}

export function conflictRate(employee) {
  if (!employee?.meetingsTotal) return 0;
  return clamp(employee.meetingsOutside / employee.meetingsTotal);
}

export function loadRate(employee) {
  if (!employee?.workHours) return 0;
  return clamp(employee.busyHours / employee.workHours);
}

export function actualityScore(employee) {
  const daysPenalty = clamp(daysSince(employee?.updatedAt) / MAX_DAYS_WITHOUT_UPDATE) * 0.55;
  const conflictPenalty = conflictRate(employee) * 0.22;
  const timezonePenalty = employee?.timezoneMismatch ? 0.10 : 0;
  const hrPenalty = employee?.hrCalendarMismatch ? 0.13 : 0;
  return clamp(1 - daysPenalty - conflictPenalty - timezonePenalty - hrPenalty);
}

export function riskScore(employee) {
  const risk = 0.34 * (1 - actualityScore(employee))
    + 0.24 * conflictRate(employee)
    + 0.24 * loadRate(employee)
    + 0.08 * (employee?.timezoneMismatch ? 1 : 0)
    + 0.10 * (employee?.hrCalendarMismatch ? 1 : 0);
  return clamp(risk);
}

export function percent(value) {
  return Math.round(clamp(value) * 100);
}

export function riskLevel(employee) {
  const value = riskScore(employee);
  if (value >= 0.75) return { label: 'Критический', tone: 'critical' };
  if (value >= 0.55) return { label: 'Высокий', tone: 'high' };
  if (value >= 0.35) return { label: 'Средний', tone: 'medium' };
  return { label: 'Низкий', tone: 'low' };
}

export function employeeStatus(employee) {
  const days = daysSince(employee?.updatedAt);
  if (riskScore(employee) >= 0.75) return 'Критический риск';
  if (loadRate(employee) >= 0.8) return 'Перегружен';
  if (employee?.meetingsOutside > 0) return 'Есть конфликт';
  if (days > MAX_DAYS_WITHOUT_UPDATE) return 'Устарел';
  return 'Актуален';
}

export function summaryMetrics(employees = [], events = []) {
  const current = employees.filter((employee) => actualityScore(employee) >= 0.7).length;
  const outdated = employees.filter((employee) => daysSince(employee.updatedAt) > MAX_DAYS_WITHOUT_UPDATE).length;
  const highRisk = employees.filter((employee) => riskScore(employee) >= 0.55).length;
  const averageLoad = employees.length ? employees.reduce((sum, employee) => sum + loadRate(employee), 0) / employees.length : 0;

  return {
    total: employees.length,
    current,
    outdated,
    highRisk,
    conflicts: events.length,
    averageLoad: percent(averageLoad)
  };
}

function employeeWorkDays(employee) {
  return employee?.workDays || employee?.work_days || [];
}

function employeeWorkStart(employee) {
  if (Number.isFinite(employee?.workStart)) return employee.workStart;
  if (typeof employee?.work_start === 'string') return Number(employee.work_start.slice(0, 2));
  return 9;
}

function employeeWorkEnd(employee) {
  if (Number.isFinite(employee?.workEnd)) return employee.workEnd;
  if (typeof employee?.work_end === 'string') return Number(employee.work_end.slice(0, 2));
  return 18;
}

function eventEmployeeId(event) {
  return Number(event.employeeId ?? event.employee_id);
}

function eventDay(event) {
  if (event.day) return event.day;
  if (!event.start_datetime) return '';
  const start = new Date(event.start_datetime);
  return ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][start.getDay()];
}

function eventHourRange(event) {
  if (event.time) {
    const match = String(event.time).match(/(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})/);
    if (match) return [Number(match[1]), Number(match[3]) || Number(match[1]) + 1];
  }
  if (event.start_datetime && event.end_datetime) {
    const start = new Date(event.start_datetime);
    const end = new Date(event.end_datetime);
    return [start.getHours(), Math.max(start.getHours() + 1, end.getHours() + (end.getMinutes() > 0 ? 1 : 0))];
  }
  return [null, null];
}

function blockingEvent(employee, events, day, hour) {
  return events.find((event) => {
    if (eventEmployeeId(event) !== Number(employee.id)) return false;
    if (eventDay(event) !== day) return false;
    const [startHour, endHour] = eventHourRange(event);
    return startHour !== null && hour >= startHour && hour < endHour;
  });
}

export function buildAvailability(employees = []) {
  return buildAvailabilityWithEvents(employees, []);
}

export function buildAvailabilityWithEvents(employees = [], events = []) {
  return DAYS.map((day) => ({
    day,
    slots: HOURS.map((hour) => {
      const missingDetails = [];
      const availableEmployees = employees.filter((employee) => {
        if (!employeeWorkDays(employee).includes(day)) {
          missingDetails.push({ employee: employee.name, reason: 'нерабочий день' });
          return false;
        }
        if (hour < employeeWorkStart(employee) || hour >= employeeWorkEnd(employee)) {
          missingDetails.push({ employee: employee.name, reason: 'вне рабочего времени' });
          return false;
        }
        const event = blockingEvent(employee, events, day, hour);
        if (event) {
          missingDetails.push({ employee: employee.name, reason: `занят: ${event.title || 'встреча'}` });
          return false;
        }
        if (loadRate(employee) >= 0.95) {
          missingDetails.push({ employee: employee.name, reason: 'перегруз' });
          return false;
        }
        return true;
      });

      let type = 'weak';
      if (availableEmployees.length === employees.length && employees.length) type = 'all';
      else if (availableEmployees.length >= Math.ceil(employees.length * 0.65)) type = 'majority';

      return {
        hour,
        count: availableEmployees.length,
        type,
        missing: missingDetails.map((item) => item.employee),
        missingDetails
      };
    })
  }));
}

export function bestSlots(employees, events = []) {
  return buildAvailabilityWithEvents(employees, events)
    .flatMap((row) => row.slots.map((slot) => ({ ...slot, day: row.day })))
    .sort((a, b) => b.count - a.count || a.hour - b.hour)
    .slice(0, 3)
    .map((slot) => ({
      label: `${slot.day}, ${slot.hour}:00-${slot.hour + 1}:00`,
      count: slot.count,
      missing: slot.missing,
      missingDetails: slot.missingDetails || []
    }));
}

export function makeRecommendations(employees = [], events = []) {
  const recommendations = [];

  employees.forEach((employee) => {
    if (riskScore(employee) >= 0.55) {
      recommendations.push({
        type: 'График',
        title: `Попросить ${employee.name} подтвердить рабочий график`,
        reason: `Риск ${percent(riskScore(employee))}%, обновление было ${daysSince(employee.updatedAt)} дней назад.`,
        priority: riskScore(employee) >= 0.75 ? 'Срочно' : 'Важно'
      });
    }

    if (employee.timezoneMismatch) {
      recommendations.push({
        type: 'Часовой пояс',
        title: `Проверить часовой пояс: ${employee.name}`,
        reason: 'Фактическая активность отличается от заявленного часового пояса.',
        priority: 'Важно'
      });
    }

    if (loadRate(employee) >= 0.8) {
      recommendations.push({
        type: 'Нагрузка',
        title: `Не назначать новые встречи: ${employee.name}`,
        reason: `Загрузка ${percent(loadRate(employee))}%, сотрудник близок к перегрузу.`,
        priority: 'Срочно'
      });
    }
  });

  events.slice(0, 2).forEach((event) => {
    recommendations.push({
      type: 'Встреча',
      title: `Перенести: ${event.title}`,
      reason: `${event.employee || 'Сотрудник'}, ${event.day || ''} ${event.time || ''}. ${event.reason || ''}`,
      priority: event.severity === 'Высокая' ? 'Срочно' : 'Важно'
    });
  });

  return recommendations;
}
