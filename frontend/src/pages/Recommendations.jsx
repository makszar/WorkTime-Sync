import RecommendationCard from '../components/RecommendationCard';

export default function Recommendations({ recommendations, roadmap }) {
  return (
    <section className="page fadeIn">
      <div className="pageHeader">
        <div>
          <span className="eyebrow">Рекомендации</span>
          <h1>Что нужно сделать в первую очередь</h1>
          <p>Экран превращает диагностику в конкретные действия для HR, PM и руководителя.</p>
        </div>
      </div>

      <div className="cardsGrid">
        {recommendations.map((item) => (
          <RecommendationCard item={item} key={`${item.title}-${item.reason}`} />
        ))}
      </div>

      <div className="panel roadmapPanel">
        <div className="panelHeader">
          <h2>Дорожная карта актуализации</h2>
          <span>план действий</span>
        </div>
        <div className="roadmap">
          {roadmap.map((item) => (
            <article className="roadmapItem" key={item.step}>
              <b>{item.step}</b>
              <div>
                <h3>{item.title}</h3>
                <p>{item.owner} - {item.deadline}</p>
              </div>
              <span>{item.state}</span>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
