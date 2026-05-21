import { useEffect, useState } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import EmployeeProfile from './pages/EmployeeProfile';
import Conflicts from './pages/Conflicts';
import Availability from './pages/Availability';
import Recommendations from './pages/Recommendations';
import { loadWorktimeData, loginUser } from './api/worktimeApi';

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

  return (
    <main className="loginPage">
      <section className="loginCard fadeIn">
        <div className="loginBrand">WorkTime-Sync</div>
        <span className="eyebrow">Вход руководителя отдела</span>
        <h1>Авторизуйтесь, чтобы открыть своих синтетических сотрудников</h1>
        <p>В демо 5 руководителей и 25 синтетических подчинённых, по 5 человек в каждом отделе.</p>

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
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) return;

    setData(null);
    setError('');
    loadWorktimeData(user)
      .then(setData)
      .catch((requestError) => setError(requestError.message));
  }, [user]);

  function handleLogin(nextUser) {
    localStorage.setItem('worktimeUser', JSON.stringify(nextUser));
    setUser(nextUser);
    setPage('dashboard');
  }

  function handleLogout() {
    localStorage.removeItem('worktimeUser');
    setUser(null);
    setData(null);
    setSelectedEmployeeId(null);
    setPage('dashboard');
  }

  function openEmployee(id) {
    setSelectedEmployeeId(id);
    setPage('profile');
  }

  if (!user) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  if (error) {
    return <div className="centerState">Ошибка загрузки данных: {error}</div>;
  }

  if (!data) {
    return <div className="centerState">Загружаем WorkTime-Sync...</div>;
  }

  const selectedEmployee = data.employees.find((employee) => employee.id === selectedEmployeeId) || data.employees[0];

  return (
    <Layout page={page} setPage={setPage} user={user} onLogout={handleLogout}>
      {page === 'dashboard' && <Dashboard data={data} setPage={setPage} />}
      {page === 'employees' && <Employees employees={data.employees} onOpen={openEmployee} department={user.department} />}
      {page === 'profile' && selectedEmployee && (
        <EmployeeProfile
          employee={selectedEmployee}
          events={data.events}
          recommendations={data.recommendations}
          goBack={() => setPage('employees')}
        />
      )}
      {page === 'conflicts' && <Conflicts events={data.events} />}
      {page === 'availability' && <Availability employees={data.employees} slots={data.bestSlots} />}
      {page === 'recommendations' && <Recommendations recommendations={data.recommendations} roadmap={data.roadmap} />}
    </Layout>
  );
}
