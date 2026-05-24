import StatCard from '../components/StatCard';
import TaskStatusBadge from '../components/TaskStatusBadge';
import { percent, riskScore } from '../utils/calculations';

function getTeams(analytics, overview) {
  if (analytics?.teams?.length) return analytics.teams;
  if (analytics?.tasksByDepartment?.length) return analytics.tasksByDepartment;
  return overview.departments?.map((department) => ({ department: department.name, employees: department.count, avg_risk: 0, total_conflicts: 0 })) || [];
}

export default function ExecutiveDashboard({ analytics, overview, setPage }) {
  const teams = getTeams(analytics, overview);
  const topRisk = analytics?.topRiskEmployees || [...(overview.employees || [])].sort((a, b) => riskScore(b) - riskScore(a)).slice(0, 5);
  const summary = analytics?.summary || overview.summary;
  const taskCounts = analytics?.taskStatusCounts || overview.taskStatusCounts || {};

  return (
    <section className="page fadeIn">
      <div className="pageHeader heroHeader">
        <div>
          <span className="eyebrow">Executive dashboard</span>
          <h1>Видимость по всей компании, отделам, рискам и задачам</h1>
          <p>Экран подключён к /analytics/company и показывает общий контур контроля: сотрудники, риск, подтверждения графиков и задачи.</p>
        </div>
        <button className="primaryButton big iconTextButton" type="button" onClick={() => setPage('tasks')}>
          <img src="/icons/brief.svg" alt="" />
          <span>Открыть задачи</span>
        </button>
      </div>

      <div className="statsGrid">
        <StatCard label="Сотрудников" value={summary?.total || summary?.total_employees || overview.totalSyntheticEmployees || 0} hint="В синтетической компании" />
        <StatCard label="Средний риск" value={`${percent(summary?.avg_risk ?? 0)}%`} hint="По всем отделам" tone="warning" />
        <StatCard label="Конфликты" value={summary?.conflicts || summary?.total_conflicts || summary?.calendar_conflicts || 0} hint="Встречи вне рабочего времени" tone="warning" />
        <StatCard label="Pending задач" value={analytics?.pendingTasks ?? taskCounts.pending ?? 0} hint="Ожидают ответа" tone="danger" />
        <StatCard label="Подтверждение графиков" value={`${percent(analytics?.scheduleConfirmationRate ?? 0)}%`} hint="По компании" tone="success" />
        <StatCard label="Отделов" value={teams.length} hint="Сравнение ниже" />
      </div>

      <div className="twoColumns wideFirst">
        <article className="panel">
          <div className="panelHeader">
            <h2>Сравнение отделов</h2>
            <span>{teams.length} отделов</span>
          </div>
          <div className="tableWrap">
            <table>
              <thead><tr><th>Отдел</th><th>Сотрудников</th><th>Средний риск</th><th>Конфликты</th><th>Задач</th></tr></thead>
              <tbody>
                {teams.map((team) => (
                  <tr key={team.department || team.team}>
                    <td>{team.department || team.team}</td>
                    <td>{team.employees}</td>
                    <td>{percent(team.avg_risk || 0)}%</td>
                    <td>{team.total_conflicts || team.outsideWorkMeetings || 0}</td>
                    <td>{team.total || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <h2>Статусы задач</h2>
            <span>по компании</span>
          </div>
          <div className="statusStack">
            {Object.entries(taskCounts).map(([status, count]) => (
              <div className="statusLine" key={status}><TaskStatusBadge status={status} /><strong>{count}</strong></div>
            ))}
          </div>
        </article>
      </div>

      <article className="panel">
        <div className="panelHeader">
          <h2>Топ сотрудников по риску</h2>
          <span>для управленческого контроля</span>
        </div>
        <div className="cardsGrid smallCards">
          {topRisk.map((employee) => (
            <article className="slotCard" key={employee.id}>
              <span>{employee.team}</span>
              <h3>{employee.name}</h3>
              <p>{employee.role}</p>
              <strong>{percent(riskScore(employee))}% риска</strong>
            </article>
          ))}
        </div>
      </article>
    </section>
  );
}
