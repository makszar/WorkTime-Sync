# Сводка обновлений WorkTime Sync

## Что изменилось в актуальной версии

1. Основной источник данных перенесён в `data/synthetic`.
2. Backend теперь читает CSV/JSON из `data/synthetic`.
3. `backend/data` оставлен как fallback.
4. Добавлена нормализация строковых id:
   - `emp001`;
   - `evt001`;
   - `abs001`.
5. Добавлена нормализация datetime с timezone offsets.
6. В данных теперь 10 сотрудников.
7. В данных 37 календарных событий.
8. HR-профили и отсутствия хранятся в CSV.
9. Добавлены/актуализированы backend endpoint'ы:
   - `/employees/{employee_id}/risk-explanation`;
   - `/analytics/groups`;
   - `/notifications`.
10. Backend поддерживает рекомендации, уведомления, группы и объяснение риска.
11. Есть GitHub Actions deploy workflow.
12. Публичный сайт показывает основной MVP: дашборд, сотрудники, карточка, конфликты, доступность, рекомендации.

## Какие файлы обновлять в репозитории

Рекомендуемые пути:

```text
README.md
presentation/presentation_draft.md
tests/test_cases.md
docs/missing_information.md
docs/repo_update_summary.md
```

Файл `README.md` нужно заменить в корне репозитория.

Остальные файлы лучше положить в соответствующие папки:

```text
presentation/presentation_draft.md
tests/test_cases.md
docs/missing_information.md
docs/repo_update_summary.md
```
