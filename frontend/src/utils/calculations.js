const MAX_DAYS_WITHOUT_UPDATE = 90;

export function clamp(value, min = 0, max = 1) {
  return Math.min(Math.max(value, min), max);
}

export function daysSince(dateString) {
  const today = new Date('2026-05-19T12:00:00');
  const target = new Date(`${dateString}T12:00:00`);
  const diff = today.getTime() - target.getTime();
  return Math.max(0, Math.round(diff / (1000 * 60 * 60 * 24)));
}

export function conflictRate(employee) {
  if (!employee.meetingsTotal) return 0;
  return clamp(employee.meetingsOutside / employee.meetingsTotal);
}

export function loadRate(employee) {
  if (!employee.workHours) return 0;
  return clamp(employee.busyHours / employee.workHours);
}

export function actualityScore(employee) {
  const daysPenalty = clamp(daysSince(employee.updatedAt) / MAX_DAYS_WITHOUT_UPDATE) * 0.55;
  const conflictPenalty = conflictRate(employee) * 0.22;
  const timezonePenalty = employee.timezoneMismatch ? 0.10 : 0;
  const hrPenalty = employee.hrCalendarMismatch ? 0.13 : 0;
  return clamp(1 - daysPenalty - conflictPenalty - timezonePenalty - hrPenalty);
}

export function riskScore(employee) {
  const risk = 0.34 * (1 - actualityScore(employee))
    + 0.24 * conflictRate(employee)
    + 0.24 * loadRate(employee)
    + 0.08 * employee.timezoneMismatch
    + 0.10 * employee.hrCalendarMismatch;
  return clamp(risk);
}

export function percent(value) {
  return Math.round(value * 100);
}

export function riskLevel(employee) {
  const value = riskScore(employee);
  if (value >= 0.75) return { label: 'Критический', tone: 'critical' };
  if (value >= 0.55) return { label: 'Высокий', tone: 'high' };
  if (value >= 0.35) return { label: 'Средний', tone: 'medium' };
  return { label: 'Низкий', tone: 'low' };
}

export function employeeStatus(employee) {
  const days = daysSince(employee.updatedAt);
  if (riskScore(employee) >= 0.75) return 'Критический риск';
  if (loadRate(employee) >= 0.8) return 'Перегружен';
  if (employee.meetingsOutside > 0) return 'Есть конфликт';
  if (days > MAX_DAYS_WITHOUT_UPDATE) return 'Устарел';
  return 'Актуален';
}

export function summaryMetrics(employees, events) {
  const current = employees.filter((employee) => actualityScore(employee) >= 0.7).length;
  const outdated = employees.filter((employee) => daysSince(employee.updatedAt) > MAX_DAYS_WITHOUT_UPDATE).length;
  const highRisk = employees.filter((employee) => riskScore(employee) >= 0.55).length;
  const averageLoad = employees.reduce((sum, employee) => sum + loadRate(employee), 0) / employees.length;

  return {
    total: employees.length,
    current,
    outdated,
    highRisk,
    conflicts: events.length,
    averageLoad: percent(averageLoad)
  };
}

function eventBlocksSlot(event, employee, day, hour) {
  const eventEmployeeId = Number(event.employeeId ?? event.employee_id);
  if (eventEmployeeId !== Number(employee.id)) return false;

  if (event.start_datetime && event.end_datetime) {
    const start = new Date(event.start_datetime);
    const end = new Date(event.end_datetime);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return false;
    const eventDay = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][start.getDay()];
    const startHour = start.getHours() + start.getMinutes() / 60;
    const endHour = end.getHours() + end.getMinutes() / 60;
    return eventDay === day && startHour < hour + 1 && endHour > hour;
  }

  if (event.day && event.time) {
    const [startText, endText] = String(event.time).split('-');
    const startHour = Number(startText?.split(':')?.[0]);
    const endHour = Number(endText?.split(':')?.[0]);
    return event.day === day && startHour < hour + 1 && endHour > hour;
  }

  return false;
}

export function buildAvailability(employees, events = []) {
  const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'];
  const hours = Array.from({ length: 13 }, (_, index) => index + 8);

  return days.map((day) => ({
    day,
    slots: hours.map((hour) => {
      const missingDetails = [];
      const availableEmployees = employees.filter((employee) => {
        let reason = '';
        if (!employee.workDays.includes(day)) reason = 'нерабочий день';
        else if (hour < employee.workStart || hour >= employee.workEnd) reason = 'вне рабочего времени';
        else if (loadRate(employee) >= 0.95) reason = 'перегруз';
        else if (events.some((event) => eventBlocksSlot(event, employee, day, hour))) reason = 'занят встречей';

        if (reason) {
          missingDetails.push({ employee: employee.name, reason });
          return false;
        }

        return true;
      });

      let type = 'weak';
      if (availableEmployees.length === employees.length && employees.length) type = 'all';
      else if (availableEmployees.length >= Math.ceil(employees.length * 0.65)) type = 'majority';

      const missing = employees.filter((employee) => !availableEmployees.includes(employee)).map((employee) => employee.name);

      return {
        hour,
        count: availableEmployees.length,
        type,
        missing,
        missingDetails
      };
    })
  }));
}

export function bestSlots(employees) {
  return buildAvailability(employees)
    .flatMap((row) => row.slots.map((slot) => ({ ...slot, day: row.day })))
    .sort((a, b) => b.count - a.count || a.hour - b.hour)
    .slice(0, 3)
    .map((slot) => ({
      label: `${slot.day}, ${slot.hour}:00-${slot.hour + 1}:00`,
      count: slot.count,
      missing: slot.missing
    }));
}

export function makeRecommendations(employees, events) {
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
      reason: `${event.employee}, ${event.day} ${event.time}. ${event.reason}`,
      priority: event.severity === 'Высокая' ? 'Срочно' : 'Важно'
    });
  });

  return recommendations;
}
