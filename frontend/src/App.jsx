import { useEffect, useMemo, useState } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import HRDashboard from './pages/HRDashboard';
import EmployeeCabinet from './pages/EmployeeCabinet';
import Tasks from './pages/Tasks';
import Employees from './pages/Employees';
import EmployeeProfile from './pages/EmployeeProfile';
import Conflicts from './pages/Conflicts';
import Availability from './pages/Availability';
import Recommendations from './pages/Recommendations';
import {
  applyTask,
  confirmSchedule,
  createTask,
  loadCompanyAnalytics,
  loadEmployeeCabinet,
  loadHrDashboard,
  loadAvailability,
  loadMyTasks,
  loadTasks,
  loadWorktimeData,
  loginUser,
  generateTasksFromConflicts,
  updateTaskStatus
} from './api/worktimeApi';

const DEMO_ACCOUNTS = [
  ['Полный руководитель', 'executive_demo', 'test0'],
  ['HR', 'hr_demo', 'testhr'],
  ['Core Platform', 'zarix', 'i9VUibm6'],
  ['Product UI', 'lixxxa', 'test1'],
  ['People Ops', 'baftype', 'test2'],
  ['Delivery', 'ssdshkaaa', 'test3'],
  ['Quality', 'agentemy', 'test4'],
  ['Сотрудник', 'gleb_employee', 'emp5']
];

function defaultPageFor(user) {
  if (user?.role === 'executive') return 'executive';
  if (user?.role === 'hr') return 'hr';
  if (user?.role === 'employee') return 'employee';
  return 'dashboard';
}

function LoginScreen({ onLogin }) {
  const [form, setForm] = useState({ login: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const user = await loginUser(form);
      onLogin(user);
    } catch (requestError) {
      setError(requestError.message || 'Не удалось войти');
    } finally {
      setIsLoading(false);
    }
  }

  function fill(login, password) {
    setForm({ login, password });
  }

  return (
    <main className="loginPage">
      <section className="loginCard fadeIn">
        <div className="loginBrand">WorkTime-Sync <span className="versionBadge">v2.6</span></div>
        <span className="eyebrow">Вход по роли</span>
        <h1>Откройте нужный контур: компания, HR, отдел или личный кабинет сотрудника</h1>
        <p>Фронтенд подключён к role-based API: user_id, demo-token, задачи, подтверждения графика и аналитика.</p>

        <form className="loginForm" onSubmit={submit}>
          <label>
            <span>Логин</span>
            <input
              value={form.login}
              onChange={(event) => setForm((current) => ({ ...current, login: event.target.value }))}
              placeholder="zarix"
              autoComplete="username"
            />
          </label>
          <label>
            <span>Пароль</span>
            <input
              value={form.password}
              onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
              placeholder="••••••••"
              type="password"
              autoComplete="current-password"
            />
          </label>

          {error && <div className="loginError">{error}</div>}

          <button className="primaryButton loginButton" type="submit" disabled={isLoading}>
            {isLoading ? 'Проверяем...' : 'Войти'}
          </button>
        </form>

        <div className="demoAccounts">
          <h2>Demo-профили</h2>
          <div className="demoGrid">
            {DEMO_ACCOUNTS.map(([role, login, password]) => (
              <button type="button" className="demoAccount" key={login} onClick={() => fill(login, password)}>
                <span>{role}</span>
                <strong>{login}</strong>
                <small>{password}</small>
              </button>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(null);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('worktimeUser');
    return saved ? JSON.parse(saved) : null;
  });
  const [data, setData] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [companyAnalytics, setCompanyAnalytics] = useState(null);
  const [hrDashboard, setHrDashboard] = useState(null);
  const [employeeCabinet, setEmployeeCabinet] = useState(null);
  const [availabilityRows, setAvailabilityRows] = useState([]);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  async function reloadAll(currentUser = user) {
    if (!currentUser) return;

    setData(null);
    setError('');
    setNotice('');

    try {
      const overview = await loadWorktimeData(currentUser);
      setData(overview);
      setAvailabilityRows(await loadAvailability(currentUser, overview.employees || []));

      const tasksLoader = currentUser.role === 'employee' ? loadMyTasks : loadTasks;
      setTasks(await tasksLoader(currentUser));

      if (currentUser.role === 'executive') {
        setCompanyAnalytics(await loadCompanyAnalytics(currentUser));
      } else {
        setCompanyAnalytics(null);
      }

      if (currentUser.role === 'hr') {
        setHrDashboard(await loadHrDashboard(currentUser));
      } else {
        setHrDashboard(null);
      }

      if (currentUser.role === 'employee') {
        setEmployeeCabinet(await loadEmployeeCabinet(currentUser));
      } else {
        setEmployeeCabinet(null);
      }
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  useEffect(() => {
    reloadAll(user);
  }, [user]);

  function handleLogin(nextUser) {
    localStorage.setItem('worktimeUser', JSON.stringify(nextUser));
    setUser(nextUser);
    setPage(defaultPageFor(nextUser));
  }

  function handleLogout() {
    localStorage.removeItem('worktimeUser');
    setUser(null);
    setData(null);
    setTasks([]);
    setSelectedEmployeeId(null);
    setPage('dashboard');
  }

  function openEmployee(id) {
    setSelectedEmployeeId(id);
    setPage('profile');
  }

  async function handleCreateTask(payload) {
    try {
      await createTask(user, payload);
      setNotice('Задача создана');
      await reloadAll(user);
    } catch (requestError) {
      setNotice(requestError.message || 'Не удалось создать задачу');
    }
  }

  async function handleTaskStatusChange(taskId, payload) {
    try {
      await updateTaskStatus(user, taskId, payload);
      setNotice('Статус задачи обновлён');
      await reloadAll(user);
    } catch (requestError) {
      setNotice(requestError.message || 'Не удалось обновить задачу');
    }
  }


  async function handleApplyTask(taskId, payload = { action: 'apply' }) {
    try {
      await applyTask(user, taskId, payload);
      setNotice('Решение применено, данные обновлены');
      await reloadAll(user);
    } catch (requestError) {
      setNotice(requestError.message || 'Не удалось применить решение');
    }
  }

  async function handleGenerateConflictTasks(payload = {}) {
    try {
      const result = await generateTasksFromConflicts(user, payload);
      setNotice(`Создано задач: ${result.created ?? 0}`);
      await reloadAll(user);
    } catch (requestError) {
      setNotice(requestError.message || 'Не удалось создать задачи по конфликтам');
    }
  }

  async function handleConfirmSchedule(employeeId, payload) {
    try {
      await confirmSchedule(user, employeeId, payload);
      setNotice('График подтверждён');
      await reloadAll(user);
    } catch (requestError) {
      setNotice(requestError.message || 'Не удалось подтвердить график');
    }
  }

  const selectedEmployee = useMemo(() => {
    if (!data?.employees?.length) return null;
    return data.employees.find((employee) => employee.id === selectedEmployeeId) || data.employees[0];
  }, [data, selectedEmployeeId]);

  if (!user) return <LoginScreen onLogin={handleLogin} />;
  if (error) return <div className="centerState">Ошибка загрузки данных: {error}</div>;
  if (!data) return <div className="centerState">Загружаем WorkTime-Sync...</div>;

  return (
    <Layout page={page} setPage={setPage} user={user} onLogout={handleLogout}>
      {notice && <div className="noticeToast">{notice}</div>}

      {page === 'executive' && <ExecutiveDashboard analytics={companyAnalytics} overview={data} setPage={setPage} />}
      {page === 'hr' && <HRDashboard dashboard={hrDashboard} overview={data} user={user} onTaskStatusChange={handleTaskStatusChange} onApplyTask={handleApplyTask} setPage={setPage} />}
      {page === 'employee' && <EmployeeCabinet cabinet={employeeCabinet} user={user} onConfirmSchedule={handleConfirmSchedule} onTaskStatusChange={handleTaskStatusChange} />}
      {page === 'myTasks' && <Tasks user={user} tasks={tasks} employees={data.employees} events={data.events} onCreateTask={handleCreateTask} onTaskStatusChange={handleTaskStatusChange} onApplyTask={handleApplyTask} onGenerateConflictTasks={handleGenerateConflictTasks} />}
      {page === 'dashboard' && <Dashboard data={data} setPage={setPage} />}
      {page === 'employees' && <Employees employees={data.employees} onOpen={openEmployee} department={user.department || 'Все отделы'} user={user} />}
      {page === 'tasks' && <Tasks user={user} tasks={tasks} employees={data.employees} events={data.events} onCreateTask={handleCreateTask} onTaskStatusChange={handleTaskStatusChange} onApplyTask={handleApplyTask} onGenerateConflictTasks={handleGenerateConflictTasks} />}
      {page === 'profile' && selectedEmployee && (
        <EmployeeProfile
          employee={selectedEmployee}
          events={data.events}
          recommendations={data.recommendations}
          goBack={() => setPage('employees')}
        />
      )}
      {page === 'conflicts' && <Conflicts events={data.events} />}
      {page === 'availability' && <Availability employees={data.employees} events={data.events} slots={data.bestSlots} rows={availabilityRows} />}
      {page === 'recommendations' && <Recommendations recommendations={data.recommendations} roadmap={data.roadmap} />}
    </Layout>
  );
}
