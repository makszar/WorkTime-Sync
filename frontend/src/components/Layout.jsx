const navItems = [
  { id: 'dashboard', label: 'Дашборд' },
  { id: 'employees', label: 'Сотрудники' },
  { id: 'conflicts', label: 'Конфликты' },
  { id: 'availability', label: 'Доступность' },
  { id: 'recommendations', label: 'Рекомендации' }
];

export default function Layout({ page, setPage, children }) {
  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark">WS</div>
          <div>
            <div className="brandTitle">WorkTime Sync</div>
            <div className="brandSub">Актуальность рабочего времени</div>
          </div>
        </div>

        <nav className="nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`navButton ${page === item.id ? 'active' : ''}`}
              onClick={() => setPage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebarHint">
          <span>Демо MVP</span>
          <p>Моковые данные можно заменить ответами FastAPI через src/api/worktimeApi.js.</p>
        </div>
      </aside>

      <main className="content">{children}</main>
    </div>
  );
}
