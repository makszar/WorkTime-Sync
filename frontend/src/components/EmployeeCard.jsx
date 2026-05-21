import { actualityScore, employeeStatus, percent, riskLevel, riskScore } from '../utils/calculations';
import RiskMeter from './RiskMeter';
import StatusBadge from './StatusBadge';

export default function EmployeeCard({ employee, onOpen }) {
  const level = riskLevel(employee);

  return (
    <article className="employeeCard">
      <div className="employeeTop">
        <div>
          <h3>{employee.name}</h3>
          <p>{employee.role} - {employee.team}</p>
        </div>
        <StatusBadge label={level.label} tone={level.tone} />
      </div>

      <div className="employeeMeta">
        <span>{employee.format}</span>
        <span>{employee.timezone}</span>
        <span>Обновлено: {employee.updatedAt}</span>
        <span>{employeeStatus(employee)}</span>
      </div>

      <div className="miniGrid">
        <RiskMeter value={percent(riskScore(employee))} label="Интегральный риск" />
        <RiskMeter value={percent(actualityScore(employee))} label="Актуальность" />
      </div>

      <button className="primaryButton cardButton" type="button" onClick={() => onOpen(employee.id)}>
        <img src="/icons/profile.svg" alt="" />
        <span>Открыть карточку</span>
      </button>
    </article>
  );
}
