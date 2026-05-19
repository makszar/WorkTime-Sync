export default function StatCard({ label, value, hint, tone = 'default' }) {
  return (
    <article className={`statCard ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{hint}</p>
    </article>
  );
}
