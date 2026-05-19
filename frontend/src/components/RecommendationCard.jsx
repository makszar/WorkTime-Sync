export default function RecommendationCard({ item }) {
  return (
    <article className="recommendationCard">
      <div className="recommendationTop">
        <span>{item.type}</span>
        <b>{item.priority}</b>
      </div>
      <h3>{item.title}</h3>
      <p>{item.reason}</p>
    </article>
  );
}
