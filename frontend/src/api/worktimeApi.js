import { employees, calendarEvents, roadmap, users } from '../data/mockData';
import { summaryMetrics, makeRecommendations, bestSlots } from '../utils/calculations';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const FORCE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

function publicUser(user) {
  if (!user) return null;
  const { password, ...safeUser } = user;
  return safeUser;
}

function departmentFilter(user) {
  return user?.department || '';
}

function buildMockOverview(user) {
  const department = departmentFilter(user);
  const scopedEmployees = department
    ? employees.filter((employee) => employee.team === department)
    : employees;
  const employeeIds = new Set(scopedEmployees.map((employee) => employee.id));
  const scopedEvents = calendarEvents.filter((event) => employeeIds.has(event.employeeId));

  return {
    employees: scopedEmployees,
    events: scopedEvents,
    roadmap,
    summary: summaryMetrics(scopedEmployees, scopedEvents),
    recommendations: makeRecommendations(scopedEmployees, scopedEvents),
    bestSlots: bestSlots(scopedEmployees),
    departments: [...new Set(employees.map((employee) => employee.team))].map((name) => ({
      name,
      count: employees.filter((employee) => employee.team === name).length
    })),
    totalSyntheticEmployees: employees.length,
    totalDemoPeople: employees.length + users.length
  };
}

function normalizeSummary(summary, scopedEmployees, events) {
  if (!summary) {
    return summaryMetrics(scopedEmployees, events);
  }

  if (summary.total !== undefined) {
    return summary;
  }

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
  const department = departmentFilter(user);
  const scopedEmployees = department
    ? (payload.employees || []).filter((employee) => employee.team === department)
    : (payload.employees || []);
  const employeeIds = new Set(scopedEmployees.map((employee) => employee.id));
  const events = (payload.events || payload.conflicts || []).filter((event) => employeeIds.has(event.employeeId));

  return {
    employees: scopedEmployees,
    events,
    roadmap: payload.roadmap || roadmap,
    summary: normalizeSummary(payload.summary, scopedEmployees, events),
    recommendations: payload.recommendations || makeRecommendations(scopedEmployees, events),
    bestSlots: payload.bestSlots || payload.best_slots || bestSlots(scopedEmployees),
    departments: payload.departments || [...new Set((payload.employees || []).map((employee) => employee.team))].map((name) => ({
      name,
      count: (payload.employees || []).filter((employee) => employee.team === name).length
    })),
    totalSyntheticEmployees: payload.totalSyntheticEmployees || payload.total_synthetic_employees || (payload.employees || []).length,
    totalDemoPeople: payload.totalDemoPeople || payload.total_demo_people || ((payload.totalSyntheticEmployees || payload.total_synthetic_employees || (payload.employees || []).length) + 5)
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

      return response.user;
    } catch (error) {
      // For local demos without a running backend we fall back to the same demo accounts.
    }
  }

  const user = users.find((item) => item.login === login && item.password === password);
  if (!user) {
    throw new Error('Неверный логин или пароль');
  }

  return publicUser(user);
}

export async function loadWorktimeData(user) {
  if (!FORCE_MOCK_DATA) {
    try {
      const department = departmentFilter(user);
      const query = department ? `?department=${encodeURIComponent(department)}` : '';
      const payload = await request(`/api/worktime/overview${query}`);
      return normalizeOverview(payload, user);
    } catch (error) {
      // The frontend remains demo-ready even if FastAPI is not running locally.
    }
  }

  return buildMockOverview(user);
}
