import RoleBadge from './RoleBadge';

const NAV_BY_ROLE = {
  executive: [
    { id: 'executive', label: 'Компания', icon: 'companies.svg' },
    { id: 'employees', label: 'Сотрудники', icon: 'candidates.svg' },
    { id: 'tasks', label: 'Задачи', icon: 'brief.svg' },
    { id: 'availability', label: 'Доступность', icon: 'calendar.svg' },
    { id: 'recommendations', label: 'Рекомендации', icon: 'notifications.svg' }
  ],
  hr: [
    { id: 'hr', label: 'HR-панель', icon: 'work.svg' },
    { id: 'employees', label: 'Сотрудники', icon: 'candidates.svg' },
    { id: 'tasks', label: 'Задачи', icon: 'brief.svg' },
    { id: 'conflicts', label: 'Конфликты', icon: 'notifications.svg' },
    { id: 'recommendations', label: 'Рекомендации', icon: 'messages.svg' }
  ],
  department_manager: [
    { id: 'dashboard', label: 'Дашборд', icon: 'home.svg' },
    { id: 'employees', label: 'Сотрудники', icon: 'candidates.svg' },
    { id: 'tasks', label: 'Задачи', icon: 'brief.svg' },
    { id: 'conflicts', label: 'Конфликты', icon: 'notifications.svg' },
    { id: 'availability', label: 'Доступность', icon: 'calendar.svg' },
    { id: 'recommendations', label: 'Рекомендации', icon: 'messages.svg' }
  ],
  employee: [
    { id: 'employee', label: 'Мой кабинет', icon: 'profile.svg' },
    { id: 'myTasks', label: 'Мои задачи', icon: 'brief.svg' },
    { id: 'availability', label: 'Окна команды', icon: 'calendar.svg' }
  ]
};

function homePageFor(user) {
  if (user?.role === 'executive') return 'executive';
  if (user?.role === 'hr') return 'hr';
  if (user?.role === 'employee') return 'employee';
  return 'dashboard';
}

export default function Layout({ page, setPage, children, user, onLogout }) {
  const navItems = NAV_BY_ROLE[user?.role] || NAV_BY_ROLE.department_manager;

  return (
    <div className="appShell">
      <header className="topbar">
        <div className="brandBlock" onClick={() => setPage(homePageFor(user))} role="button" tabIndex={0}>
          <span className="brandText">WorkTime-Sync</span><span className="versionBadge">v2.5</span>
        </div>

        <nav className="nav" aria-label="Главная навигация">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`navButton ${page === item.id ? 'active' : ''}`}
              onClick={() => setPage(item.id)}
            >
              <img src={`/icons/${item.icon}`} alt="" className="navIcon" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="userBox">
          <div className="userAvatar">{(user?.name || user?.login || 'U').slice(0, 1).toUpperCase()}</div>
          <div className="userMeta">
            <strong>{user?.name || user?.login}</strong>
            <span>{user?.department || 'Вся компания'}</span>
          </div>
          <RoleBadge user={user} />
          <button className="iconButton" type="button" onClick={onLogout} title="Выйти">
            <img src="/icons/response.svg" alt="" />
          </button>
        </div>
      </header>

      <main className="content">{children}</main>
    </div>
  );
}
