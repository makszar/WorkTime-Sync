import { TASK_TYPE_LABELS } from '../api/worktimeApi';

export default function TaskTypeBadge({ type }) {
  return <span className="taskTypeBadge">{TASK_TYPE_LABELS[type] || type}</span>;
}
