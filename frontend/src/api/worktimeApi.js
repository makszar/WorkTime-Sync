import { employees, calendarEvents, roadmap } from '../data/mockData';
import { summaryMetrics, makeRecommendations, bestSlots } from '../utils/calculations';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA !== 'false';

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function loadWorktimeData() {
  if (!USE_MOCK_DATA) {
    return request('/api/worktime/overview');
  }

  return {
    employees,
    events: calendarEvents,
    roadmap,
    summary: summaryMetrics(employees, calendarEvents),
    recommendations: makeRecommendations(employees, calendarEvents),
    bestSlots: bestSlots(employees)
  };
}
