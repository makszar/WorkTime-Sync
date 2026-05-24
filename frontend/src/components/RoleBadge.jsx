const ROLE_LABELS = {
  executive: 'Полный руководитель',
  hr: 'HR',
  department_manager: 'Руководитель отдела',
  employee: 'Сотрудник'
};

export default function RoleBadge({ user }) {
  const label = user?.role_label || ROLE_LABELS[user?.role] || user?.role || 'Роль';
  return <span className={`roleBadge role-${user?.role || 'default'}`}>{label}</span>;
}
