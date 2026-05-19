export const employees = [
  {
    id: 1,
    name: 'Анна Морозова',
    role: 'HR-специалист',
    team: 'People Ops',
    format: 'Гибрид',
    timezone: 'UTC+3',
    workDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    workStart: 9,
    workEnd: 18,
    updatedAt: '2026-05-02',
    meetingsTotal: 18,
    meetingsOutside: 1,
    busyHours: 25,
    workHours: 40,
    timezoneMismatch: 0,
    hrCalendarMismatch: 0,
    exceptions: ['Нет активных исключений'],
    statusNote: 'График выглядит актуальным и подтвержден недавно.'
  },
  {
    id: 2,
    name: 'Илья Романов',
    role: 'Backend-разработчик',
    team: 'Core Platform',
    format: 'Удаленно',
    timezone: 'UTC+5',
    workDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    workStart: 10,
    workEnd: 19,
    updatedAt: '2026-01-30',
    meetingsTotal: 24,
    meetingsOutside: 7,
    busyHours: 36,
    workHours: 40,
    timezoneMismatch: 1,
    hrCalendarMismatch: 1,
    exceptions: ['2 дня командировки', 'Регулярные созвоны после 20:00'],
    statusNote: 'Есть признаки смены часового пояса и перегруза по встречам.'
  },
  {
    id: 3,
    name: 'Мария Ким',
    role: 'Frontend-разработчик',
    team: 'Product UI',
    format: 'Офис',
    timezone: 'UTC+3',
    workDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    workStart: 8,
    workEnd: 17,
    updatedAt: '2026-04-20',
    meetingsTotal: 20,
    meetingsOutside: 3,
    busyHours: 31,
    workHours: 40,
    timezoneMismatch: 0,
    hrCalendarMismatch: 1,
    exceptions: ['Личные часы в среду 14:00-16:00'],
    statusNote: 'Часть календаря не совпадает с HR-графиком.'
  },
  {
    id: 4,
    name: 'Дмитрий Волков',
    role: 'Проектный менеджер',
    team: 'Delivery',
    format: 'Гибрид',
    timezone: 'UTC+3',
    workDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    workStart: 9,
    workEnd: 18,
    updatedAt: '2025-12-15',
    meetingsTotal: 32,
    meetingsOutside: 9,
    busyHours: 39,
    workHours: 40,
    timezoneMismatch: 0,
    hrCalendarMismatch: 1,
    exceptions: ['Перегруз по встречам', 'Данные не подтверждались больше 90 дней'],
    statusNote: 'Высокий риск неактуальности и перегруз по встречам.'
  },
  {
    id: 5,
    name: 'Олег Сафин',
    role: 'QA-инженер',
    team: 'Quality',
    format: 'Удаленно',
    timezone: 'UTC+4',
    workDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    workStart: 11,
    workEnd: 20,
    updatedAt: '2026-03-12',
    meetingsTotal: 14,
    meetingsOutside: 2,
    busyHours: 22,
    workHours: 40,
    timezoneMismatch: 1,
    hrCalendarMismatch: 0,
    exceptions: ['Часовой пояс отличается от основной команды'],
    statusNote: 'Нужно проверить часовой пояс перед планированием общих встреч.'
  },
  {
    id: 6,
    name: 'Екатерина Лебедева',
    role: 'Бизнес-аналитик',
    team: 'Discovery',
    format: 'Офис',
    timezone: 'UTC+3',
    workDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    workStart: 9,
    workEnd: 18,
    updatedAt: '2026-05-10',
    meetingsTotal: 16,
    meetingsOutside: 0,
    busyHours: 21,
    workHours: 40,
    timezoneMismatch: 0,
    hrCalendarMismatch: 0,
    exceptions: ['Отпуск запланирован через 2 недели'],
    statusNote: 'Данные свежие, конфликтов нет.'
  }
];

export const calendarEvents = [
  {
    id: 1,
    employeeId: 2,
    employee: 'Илья Романов',
    title: 'Синхронизация с командой продукта',
    day: 'Вт',
    time: '20:30-21:15',
    reason: 'Встреча назначена позже рабочего интервала сотрудника.',
    severity: 'Высокая'
  },
  {
    id: 2,
    employeeId: 4,
    employee: 'Дмитрий Волков',
    title: 'Статус по спринту',
    day: 'Ср',
    time: '08:15-09:00',
    reason: 'Событие начинается раньше заявленного рабочего времени.',
    severity: 'Средняя'
  },
  {
    id: 3,
    employeeId: 3,
    employee: 'Мария Ким',
    title: 'Дизайн-ревью',
    day: 'Ср',
    time: '17:30-18:30',
    reason: 'Часть встречи выходит за пределы рабочего графика.',
    severity: 'Средняя'
  },
  {
    id: 4,
    employeeId: 4,
    employee: 'Дмитрий Волков',
    title: 'Планирование релиза',
    day: 'Пт',
    time: '19:00-20:00',
    reason: 'Регулярное событие вне рабочего времени.',
    severity: 'Высокая'
  }
];

export const roadmap = [
  {
    step: '1',
    title: 'Подтвердить графики с высоким риском',
    owner: 'HR',
    deadline: 'Сегодня',
    state: 'Срочно'
  },
  {
    step: '2',
    title: 'Проверить часовые пояса распределенной команды',
    owner: 'Руководитель',
    deadline: 'До конца дня',
    state: 'Важно'
  },
  {
    step: '3',
    title: 'Перенести регулярные встречи вне рабочего времени',
    owner: 'PM',
    deadline: 'Завтра',
    state: 'В работе'
  }
];
