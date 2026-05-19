import EmployeeCard from '../components/EmployeeCard';
import StatusBadge from '../components/StatusBadge';
import { actualityScore, conflictRate, employeeStatus, percent, riskLevel, riskScore } from '../utils/calculations';

export default function Employees({ employees, onOpen }) {
  return (
    <section className="page fadeIn">
      <div className="pageHeader">
        <div>
          <span className="eyebrow">Сотрудники</span>
          <h1>Карточки и таблица риска</h1>
          <p>Можно быстро открыть сотрудника и понять, почему система считает график проблемным.</p>
        </div>
      </div>

      <div className="cardsGrid">
        {employees.map((employee) => (
          <EmployeeCard employee={employee} key={employee.id} onOpen={onOpen} />
        ))}
      </div>

      <div className="panel tablePanel">
        <div className="panelHeader">
          <h2>Таблица для HR и руководителя</h2>
          <span>все ключевые поля</span>
        </div>
        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                <th>Сотрудник</th>
                <th>Формат</th>
                <th>Часовой пояс</th>
                <th>Обновление</th>
                <th>Актуальность</th>
                <th>Конфликты</th>
                <th>Риск</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => {
                const level = riskLevel(employee);
                return (
                  <tr key={employee.id} onClick={() => onOpen(employee.id)}>
                    <td>{employee.name}</td>
                    <td>{employee.format}</td>
                    <td>{employee.timezone}</td>
                    <td>{employee.updatedAt}</td>
                    <td>{percent(actualityScore(employee))}%</td>
                    <td>{percent(conflictRate(employee))}%</td>
                    <td>{percent(riskScore(employee))}%</td>
                    <td><StatusBadge label={employeeStatus(employee)} tone={level.tone} /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
