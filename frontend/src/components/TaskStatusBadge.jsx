import { TASK_STATUS_LABELS } from '../api/worktimeApi';

const TONES = {
  pending: 'medium',
  confirmed: 'low',
  rejected: 'critical',
  done: 'low',
  expired: 'high',
  reschedule_requested: 'medium'
};

export default function TaskStatusBadge({ status }) {
  return <span className={`statusBadge ${TONES[status] || 'default'}`}>{TASK_STATUS_LABELS[status] || status}</span>;
}
