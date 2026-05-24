import { employees, calendarEvents, roadmap, users, mockTasks, mockScheduleConfirmations } from '../data/mockData';
import { summaryMetrics, makeRecommendations, bestSlots, riskScore, loadRate, daysSince } from '../utils/calculations';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const FORCE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';
const BACKEND_PREFIX = '/api';

function apiPath(path) {
  if (path.startsWith('/api/') || path === '/api') return path;
  if (path.startsWith('/auth/')) return path;
  return `${BACKEND_PREFIX}${path}`;
}

export const TASK_STATUS_LABELS = {
  pending: 'Ожидает действия',
  confirmed: 'Подтверждено',
  rejected: 'Отклонено',
  done: 'Закрыто',
  expired: 'Просрочено',
  reschedule_requested: 'Запрошен перенос'
};

export const TASK_TYPE_LABELS = {
  confirm_schedule: 'Подтвердить график',
  review_hr_profile: 'Проверить HR-профиль',
  review_load: 'Проверить нагрузку',
  update_timezone: 'Проверить часовой пояс',
  meeting_confirmation: 'Подтвердить встречу',
  reschedule_meeting: 'Перенести встречу',
  meeting_outside_work_approval: 'Согласовать встречу вне времени'
};

export const MEETING_ACTION_BY_TYPE = {
  meeting_confirmation: 'confirm',
  reschedule_meeting: 'reschedule',
  meeting_outside_work_approval: 'approve_outside_work'
};

function authHeaders(user) {
  return user?.token ? { Authorization: `Bearer ${user.token}` } : {};
}

function userQuery(user, extra = {}) {
  const params = new URLSearchParams();
  if (user?.id) params.set('user_id', user.id);
  Object.entries(extra).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') params.set(key, value);
  });
  const query = params.toString();
  return query ? `?${query}` : '';
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    let message = response.status === 405
      ? 'API 405: запрос попал не в backend. Проверьте, что frontend использует /api-маршруты и Nginx проксирует /api/ на FastAPI.'
      : `API error: ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch {
      // json body is optional
    }
    throw new Error(message);
  }

  return response.json();
}

function publicUser(user) {
  if (!user) return null;
  const { password, ...safeUser } = user;
  return safeUser;
}

function normalizeUser(raw, token = '') {
  if (!raw) return null;
  const role = raw.role === 'Руководитель отдела' ? 'department_manager' : raw.role;
  return {
    ...raw,
    role,
    role_label: raw.role_label || (role === 'department_manager' ? 'Руководитель отдела' : raw.role),
    scope: raw.scope || (role === 'employee' ? 'self' : role === 'department_manager' ? 'department' : 'all'),
    employee_id: raw.employee_id ?? raw.employeeId ?? null,
    token: token || raw.token || ''
  };
}

function scopedEmployeesForUser(user) {
  if (!user) return employees;
  if (user.role === 'employee') return employees.filter((employee) => employee.id === Number(user.employee_id));
  if (user.scope === 'department' || user.role === 'department_manager') {
    return employees.filter((employee) => employee.team === user.department);
  }
  return employees;
}

function normalizeEvent(event) {
  if (event.employeeId !== undefined) return event;
  const employee = employees.find((item) => item.id === Number(event.employee_id));
  const start = event.start_datetime ? new Date(event.start_datetime) : null;
  const end = event.end_datetime ? new Date(event.end_datetime) : null;
  return {
    ...event,
    employeeId: Number(event.employee_id),
    employee: employee?.name || event.employee || 'Сотрудник',
    day: event.day || (start ? ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][start.getDay()] : ''),
    time: event.time || (start && end ? `${start.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}-${end.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}` : ''),
    reason: event.reason || 'Событие требует проверки по рабочему графику.',
    severity: event.severity || 'Средняя'
  };
}

function visibleTasksForUser(user, tasks = mockTasks) {
  if (!user) return tasks;
  if (user.role === 'employee') return tasks.filter((task) => Number(task.employee_id) === Number(user.employee_id));
  if (user.scope === 'department' || user.role === 'department_manager') {
    return tasks.filter((task) => task.department === user.department || task.employee_team === user.department);
  }
  return tasks;
}

function buildMockOverview(user) {
  const scopedEmployees = scopedEmployeesForUser(user);
  const ids = new Set(scopedEmployees.map((employee) => employee.id));
  const scopedEvents = calendarEvents.filter((event) => ids.has(event.employeeId));
  const scopedTasks = visibleTasksForUser(user);

  return {
    employees: scopedEmployees,
    events: scopedEvents,
    roadmap,
    summary: summaryMetrics(scopedEmployees, scopedEvents),
    recommendations: makeRecommendations(scopedEmployees, scopedEvents),
    bestSlots: bestSlots(scopedEmployees),
    tasks: scopedTasks,
    taskStatusCounts: countByStatus(scopedTasks),
    departments: [...new Set(employees.map((employee) => employee.team))].map((name) => ({
      name,
      count: employees.filter((employee) => employee.team === name).length
    })),
    totalSyntheticEmployees: employees.length,
    totalDemoPeople: employees.length + users.length,
    currentUser: publicUser(user)
  };
}

function normalizeSummary(summary, scopedEmployees, events) {
  if (!summary) return summaryMetrics(scopedEmployees, events);
  if (summary.total !== undefined) return summary;

  return {
    total: summary.total_employees ?? scopedEmployees.length,
    current: summary.total_employees !== undefined
      ? Math.max(0, summary.total_employees - (summary.outdated_employees || 0) - (summary.high_risk_employees || 0))
      : scopedEmployees.length,
    outdated: summary.outdated_employees ?? 0,
    highRisk: summary.high_risk_employees ?? 0,
    conflicts: summary.calendar_conflicts ?? summary.total_conflicts ?? events.length,
    averageLoad: Math.round((summary.avg_load ?? 0) * 100)
  };
}

function normalizeOverview(payload, user) {
  const scopedEmployees = payload.employees || [];
  const ids = new Set(scopedEmployees.map((employee) => employee.id));
  const events = (payload.events || payload.conflicts || []).map(normalizeEvent).filter((event) => ids.has(event.employeeId));
  const totalSynthetic = payload.totalSyntheticEmployees || payload.total_synthetic_employees || payload.meta?.total_employees_count || scopedEmployees.length;

  return {
    employees: scopedEmployees,
    events,
    roadmap: payload.roadmap || roadmap,
    summary: normalizeSummary(payload.summary, scopedEmployees, events),
    recommendations: payload.recommendations || makeRecommendations(scopedEmployees, events),
    bestSlots: payload.bestSlots || payload.best_slots || bestSlots(scopedEmployees),
    tasks: payload.tasks || [],
    taskStatusCounts: payload.taskStatusCounts || countByStatus(payload.tasks || []),
    departments: payload.departments || [...new Set(scopedEmployees.map((employee) => employee.team))].map((name) => ({
      name,
      count: scopedEmployees.filter((employee) => employee.team === name).length
    })),
    totalSyntheticEmployees: totalSynthetic,
    totalDemoPeople: payload.totalDemoPeople || payload.total_demo_people || totalSynthetic + users.length,
    currentUser: payload.currentUser || publicUser(user),
    meta: payload.meta || {}
  };
}

export function countByStatus(tasks = []) {
  return tasks.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1;
    return acc;
  }, { pending: 0, confirmed: 0, rejected: 0, done: 0, expired: 0, reschedule_requested: 0 });
}

function buildMockCompanyAnalytics() {
  const overview = buildMockOverview({ role: 'executive', scope: 'all' });
  const teams = overview.departments.map((department) => {
    const teamEmployees = employees.filter((employee) => employee.team === department.name);
    const teamTasks = mockTasks.filter((task) => task.department === department.name);
    const teamConflicts = calendarEvents.filter((event) => teamEmployees.some((employee) => employee.id === event.employeeId));
    return {
      department: department.name,
      employees: teamEmployees.length,
      avg_risk: Number((teamEmployees.reduce((sum, employee) => sum + riskScore(employee), 0) / teamEmployees.length).toFixed(2)),
      total_conflicts: teamConflicts.length,
      total: teamTasks.length,
      pending: teamTasks.filter((task) => task.status === 'pending').length,
      rejected: teamTasks.filter((task) => task.status === 'rejected').length,
      done: teamTasks.filter((task) => task.status === 'done').length
    };
  });

  return {
    summary: overview.summary,
    teams,
    departments: overview.departments,
    tasksByDepartment: teams,
    taskStatusCounts: countByStatus(mockTasks),
    pendingTasks: mockTasks.filter((task) => task.status === 'pending').length,
    rejectedTasks: mockTasks.filter((task) => task.status === 'rejected').length,
    scheduleConfirmationRate: 0.48,
    confirmationByDepartment: overview.departments.map((department) => ({
      department: department.name,
      employees: department.count,
      confirmed: mockScheduleConfirmations.filter((item) => {
        const employee = employees.find((candidate) => candidate.id === item.employee_id);
        return employee?.team === department.name && item.status === 'confirmed';
      }).length,
      confirmationRate: 0.4
    })),
    worstConfirmationDepartments: [],
    outsideWorkMeetingDepartments: teams.map((item) => ({ department: item.department, outsideWorkMeetings: item.total_conflicts })),
    topRiskEmployees: [...employees].sort((a, b) => riskScore(b) - riskScore(a)).slice(0, 5)
  };
}

function buildMockHrDashboard() {
  return {
    dataMismatches: employees.filter((employee) => employee.hrCalendarMismatch || employee.timezoneMismatch).map((employee) => ({
      id: `mismatch-${employee.id}`,
      employeeId: employee.id,
      employee: employee.name,
      title: employee.timezoneMismatch ? 'Расхождение часового пояса' : 'Расхождение с HR-профилем',
      reason: employee.statusNote,
      severity: employee.hrCalendarMismatch ? 'Высокая' : 'Средняя'
    })),
    outdatedEmployees: employees.filter((employee) => daysSince(employee.updatedAt) > 90),
    employeesWithoutConfirmation: employees.filter((employee) => !mockScheduleConfirmations.some((item) => item.employee_id === employee.id && item.status === 'confirmed')),
    scheduleConfirmations: mockScheduleConfirmations,
    pendingTasks: mockTasks.filter((task) => task.status === 'pending'),
    rejectedTasks: mockTasks.filter((task) => task.status === 'rejected'),
    overdueTasks: mockTasks.filter((task) => task.status === 'pending' && task.due_date < '2026-05-19'),
    changeRequestedConfirmations: mockScheduleConfirmations.filter((item) => item.status === 'change_requested'),
    taskStatusCounts: countByStatus(mockTasks),
    confirmationByDepartment: buildMockCompanyAnalytics().confirmationByDepartment,
    dataQuality: { issues: [] }
  };
}

function buildMockEmployeeCabinet(user) {
  const employee = employees.find((item) => item.id === Number(user.employee_id)) || employees[0];
  const employeeTasks = mockTasks.filter((task) => Number(task.employee_id) === employee.id);
  const employeeEvents = calendarEvents.filter((event) => event.employeeId === employee.id);

  return {
    employee,
    frontend_employee: employee,
    tasks: employeeTasks,
    pendingTasks: employeeTasks.filter((task) => task.status === 'pending'),
    completedTasks: employeeTasks.filter((task) => ['confirmed', 'done', 'expired'].includes(task.status)),
    tasksByType: employeeTasks.reduce((acc, task) => ({ ...acc, [task.type]: (acc[task.type] || 0) + 1 }), {}),
    meetingTasks: employeeTasks.filter((task) => task.type?.startsWith('meeting') || task.type?.includes('meeting')),
    upcomingEvents: employeeEvents,
    conflictingEvents: employeeEvents,
    scheduleConfirmationStatus: mockScheduleConfirmations.find((item) => item.employee_id === employee.id)?.status || 'not_confirmed',
    metrics: employee.metrics || {
      risk: riskScore(employee),
      load: loadRate(employee),
      schedule_actuality: 1 - Math.min(daysSince(employee.updatedAt) / 90, 1)
    },
    recommendations: makeRecommendations([employee], employeeEvents)
  };
}

export async function loginUser(credentials) {
  const login = credentials.login.trim();
  const password = credentials.password;

  if (!FORCE_MOCK_DATA) {
    try {
      const response = await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ login, password })
      });
      return normalizeUser(response.user, response.token);
    } catch {
      // fallback for local frontend demos
    }
  }

  const user = users.find((item) => item.login === login && item.password === password);
  if (!user) throw new Error('Неверный логин или пароль');
  return normalizeUser(publicUser(user), `demo-${user.login}`);
}

export async function loadWorktimeData(user) {
  if (!FORCE_MOCK_DATA) {
    try {
      const payload = await request(`/api/worktime/overview${userQuery(user)}`, { headers: authHeaders(user) });
      return normalizeOverview(payload, user);
    } catch {
      // fallback
    }
  }
  return buildMockOverview(user);
}

export async function loadCompanyAnalytics(user) {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(`${apiPath('/analytics/company')}${userQuery(user)}`, { headers: authHeaders(user) });
    } catch {
      // fallback
    }
  }
  return buildMockCompanyAnalytics();
}

export async function loadHrDashboard(user) {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(`${apiPath('/analytics/hr-dashboard')}${userQuery(user)}`, { headers: authHeaders(user) });
    } catch {
      // fallback
    }
  }
  return buildMockHrDashboard();
}

export async function loadEmployeeCabinet(user) {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(`${apiPath('/employees/me')}${userQuery(user)}`, { headers: authHeaders(user) });
    } catch {
      // fallback
    }
  }
  return buildMockEmployeeCabinet(user);
}

export async function loadTasks(user, filters = {}) {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(`${apiPath('/tasks')}${userQuery(user, filters)}`, { headers: authHeaders(user) });
    } catch {
      // fallback
    }
  }
  let tasks = visibleTasksForUser(user);
  if (filters.status) tasks = tasks.filter((task) => task.status === filters.status);
  if (filters.department) tasks = tasks.filter((task) => task.department === filters.department);
  return tasks;
}

export async function loadMyTasks(user) {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(`${apiPath('/tasks/my')}${userQuery(user)}`, { headers: authHeaders(user) });
    } catch {
      // fallback
    }
  }
  return visibleTasksForUser(user);
}

export async function loadTasksMeta() {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(apiPath('/tasks/meta'));
    } catch {
      // fallback
    }
  }
  return {
    taskTypes: Object.entries(TASK_TYPE_LABELS).map(([value, label]) => ({
      value,
      label,
      requiresRelatedEvent: value.includes('meeting'),
      requiresSuggestedRange: value === 'reschedule_meeting',
      allowedMeetingActions: MEETING_ACTION_BY_TYPE[value] ? [MEETING_ACTION_BY_TYPE[value]] : []
    })),
    taskStatuses: Object.entries(TASK_STATUS_LABELS).map(([value, label]) => ({ value, label, requiresComment: ['rejected', 'reschedule_requested'].includes(value) })),
    meetingActions: [
      { value: 'confirm', label: 'Подтвердить участие' },
      { value: 'reschedule', label: 'Перенести встречу' },
      { value: 'approve_outside_work', label: 'Согласовать вне рабочего времени' }
    ]
  };
}

export async function createTask(user, payload) {
  if (!FORCE_MOCK_DATA) {
    return request(`${apiPath('/tasks')}${userQuery(user)}`, {
      method: 'POST',
      headers: authHeaders(user),
      body: JSON.stringify(payload)
    });
  }
  return { ...payload, id: Date.now(), status: 'pending', created_by_user_id: user.id, creator_name: user.name };
}

export async function updateTaskStatus(user, taskId, payload) {
  if (!FORCE_MOCK_DATA) {
    return request(`${apiPath(`/tasks/${taskId}/status`)}${userQuery(user)}`, {
      method: 'PATCH',
      headers: authHeaders(user),
      body: JSON.stringify(payload)
    });
  }
  return { id: taskId, ...payload };
}


export async function applyTask(user, taskId, payload = { action: 'apply' }) {
  if (!FORCE_MOCK_DATA) {
    return request(`${apiPath(`/tasks/${taskId}/apply`)}${userQuery(user)}`, {
      method: 'POST',
      headers: authHeaders(user),
      body: JSON.stringify(payload)
    });
  }
  return { status: 'applied', task: { id: taskId, status: 'done' } };
}

export async function generateConflictTasks(user, payload = {}) {
  if (!FORCE_MOCK_DATA) {
    return request(`${apiPath('/tasks/generate-from-conflicts')}${userQuery(user)}`, {
      method: 'POST',
      headers: authHeaders(user),
      body: JSON.stringify(payload)
    });
  }
  return { created: 0, tasks: [] };
}

export async function loadAvailability(user) {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(`${apiPath('/analytics/availability')}${userQuery(user)}`, { headers: authHeaders(user) });
    } catch {
      // fallback ниже
    }
  }
  return null;
}

export async function confirmSchedule(user, employeeId, payload) {
  if (!FORCE_MOCK_DATA) {
    return request(`${apiPath(`/employees/${employeeId}/confirm-schedule`)}${userQuery(user)}`, {
      method: 'PATCH',
      headers: authHeaders(user),
      body: JSON.stringify(payload)
    });
  }
  return { employee_id: employeeId, status: 'confirmed', comment: payload.comment || '' };
}

export async function loadRiskExplanation(user, employeeId) {
  if (!FORCE_MOCK_DATA) {
    try {
      return await request(`${apiPath(`/employees/${employeeId}/risk-explanation`)}${userQuery(user)}`, { headers: authHeaders(user) });
    } catch {
      // fallback
    }
  }
  const employee = employees.find((item) => item.id === Number(employeeId));
  return {
    employeeId,
    employee: employee?.name || 'Сотрудник',
    risk: employee ? riskScore(employee) : 0,
    riskStatus: employee ? (riskScore(employee) > 0.55 ? 'высокий' : 'средний') : 'низкий',
    formula: 'R = актуальность + конфликты + нагрузка + HR-расхождения',
    factors: [],
    recommendedActions: employee?.exceptions || []
  };
}
