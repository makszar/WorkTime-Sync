const navItems = [
  { id: 'dashboard', label: 'Дашборд', icon: 'home.svg' },
  { id: 'employees', label: 'Сотрудники', icon: 'candidates.svg' },
  { id: 'conflicts', label: 'Конфликты', icon: 'notifications.svg' },
  { id: 'availability', label: 'Доступность', icon: 'calendar.svg' },
  { id: 'recommendations', label: 'Рекомендации', icon: 'brief.svg' }
];

export default function Layout({ page, setPage, children, user, onLogout }) {
  return (
    <div className="appShell">
      <header className="topbar">
        <div className="brandText" onClick={() => setPage('dashboard')} role="button" tabIndex={0}>
          WorkTime-Sync
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
          <div className="userAvatar">{user.name.slice(0, 1).toUpperCase()}</div>
          <div className="userMeta">
            <strong>{user.name}</strong>
            <span>{user.department}</span>
          </div>
          <button className="iconButton" type="button" onClick={onLogout} title="Выйти">
            <img src="/icons/response.svg" alt="" />
          </button>
        </div>
      </header>

      <main className="content">{children}</main>
    </div>
  );
}
