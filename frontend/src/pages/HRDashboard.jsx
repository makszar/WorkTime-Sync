import StatCard from '../components/StatCard';
import TaskCard from '../components/TaskCard';

function listFrom(...items) {
  return items.find((item) => Array.isArray(item)) || [];
}

export default function HRDashboard({ dashboard, overview, user, onTaskStatusChange, onApplyTask, setPage }) {
  const mismatches = listFrom(dashboard?.dataMismatches, dashboard?.data_mismatches, dashboard?.hrMismatches);
  const outdated = listFrom(dashboard?.outdatedEmployees, dashboard?.outdated_employees);
  const withoutConfirm = listFrom(dashboard?.employeesWithoutConfirmation, dashboard?.employees_without_confirmation);
  const pendingTasks = dashboard?.pendingTasks || [];
  const rejectedTasks = dashboard?.rejectedTasks || [];
  const overdueTasks = dashboard?.overdueTasks || [];

  return (
    <section className="page fadeIn">
      <div className="pageHeader heroHeader">
        <div>
          <span className="eyebrow">HR dashboard</span>
          <h1>HR-расхождения, подтверждения графиков и проблемные задачи</h1>
          <p>Экран подключён к /analytics/hr-dashboard и помогает HR быстро увидеть, кому нужна проверка.</p>
        </div>
        <button className="primaryButton big iconTextButton" type="button" onClick={() => setPage('tasks')}>
          <img src="/icons/brief.svg" alt="" />
          <span>Создать HR-задачу</span>
        </button>
      </div>

      <div className="statsGrid">
        <StatCard label="HR-расхождения" value={mismatches.length} hint="Профиль, время, timezone" tone="danger" />
        <StatCard label="Устаревшие графики" value={outdated.length} hint="Давно не подтверждались" tone="warning" />
        <StatCard label="Без подтверждения" value={withoutConfirm.length} hint="Нужно запросить ответ" tone="warning" />
        <StatCard label="Pending задач" value={pendingTasks.length} hint="Ожидают действия" />
        <StatCard label="Rejected" value={rejectedTasks.length} hint="Нужна реакция HR" tone="danger" />
        <StatCard label="Просрочено" value={overdueTasks.length} hint="Нарушен срок" tone="danger" />
      </div>

      <div className="twoColumns">
        <article className="panel">
          <div className="panelHeader"><h2>Расхождения с HR-данными</h2><span>{mismatches.length}</span></div>
          <div className="stackList">
            {mismatches.slice(0, 8).map((item) => (
              <div className="eventItem" key={item.id || `${item.employeeId}-${item.title}`}>
                <strong>{item.employee || item.employee_name}</strong>
                <span>{item.title || item.type}</span>
                <p>{item.reason || item.description}</p>
              </div>
            ))}
            {!mismatches.length && <p className="emptyState">Критичных HR-расхождений нет.</p>}
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader"><h2>Подтверждения по отделам</h2><span>schedule confirmations</span></div>
          <div className="tableWrap">
            <table>
              <thead><tr><th>Отдел</th><th>Сотрудников</th><th>Подтвердили</th><th>Доля</th></tr></thead>
              <tbody>
                {(dashboard?.confirmationByDepartment || overview.departments || []).map((row) => (
                  <tr key={row.department || row.name}>
                    <td>{row.department || row.name}</td>
                    <td>{row.employees || row.count}</td>
                    <td>{row.confirmed ?? '-'}</td>
                    <td>{Math.round((row.confirmationRate || 0) * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <article className="panel">
        <div className="panelHeader"><h2>Задачи, требующие внимания</h2><span>{pendingTasks.length + rejectedTasks.length}</span></div>
        <div className="cardsGrid smallCards">
          {[...rejectedTasks, ...pendingTasks].slice(0, 6).map((task) => (
            <TaskCard task={task} user={user} onStatusChange={onTaskStatusChange} onApplyTask={onApplyTask} key={task.id} />
          ))}
        </div>
      </article>
    </section>
  );
}
