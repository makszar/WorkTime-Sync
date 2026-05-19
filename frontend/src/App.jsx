import { useEffect, useState } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import EmployeeProfile from './pages/EmployeeProfile';
import Conflicts from './pages/Conflicts';
import Availability from './pages/Availability';
import Recommendations from './pages/Recommendations';
import { loadWorktimeData } from './api/worktimeApi';

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadWorktimeData()
      .then(setData)
      .catch((requestError) => setError(requestError.message));
  }, []);

  function openEmployee(id) {
    setSelectedEmployeeId(id);
    setPage('profile');
  }

  if (error) {
    return <div className="centerState">Ошибка загрузки данных: {error}</div>;
  }

  if (!data) {
    return <div className="centerState">Загружаем WorkTime Sync...</div>;
  }

  const selectedEmployee = data.employees.find((employee) => employee.id === selectedEmployeeId) || data.employees[0];

  return (
    <Layout page={page} setPage={setPage}>
      {page === 'dashboard' && <Dashboard data={data} setPage={setPage} />}
      {page === 'employees' && <Employees employees={data.employees} onOpen={openEmployee} />}
      {page === 'profile' && (
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
