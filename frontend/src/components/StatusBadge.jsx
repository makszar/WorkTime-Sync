export default function StatusBadge({ label, tone = 'default' }) {
  return <span className={`statusBadge ${tone}`}>{label}</span>;
}
