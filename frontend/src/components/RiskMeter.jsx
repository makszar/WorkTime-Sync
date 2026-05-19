export default function RiskMeter({ value, label }) {
  return (
    <div className="riskMeter">
      <div className="meterTop">
        <span>{label || 'Риск'}</span>
        <strong>{value}%</strong>
      </div>
      <div className="meterTrack">
        <div className="meterFill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
