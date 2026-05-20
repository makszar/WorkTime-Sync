import pytest

from app import data_loader


def test_csv_loader_converts_semicolon_lists_and_validates(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv_path = data_dir / "employees.csv"
    csv_path.write_text(
        "id,name,team,role,timezone,work_start,work_end,work_days,work_format,last_update_date\n"
        "1,Анна,People,HR,Europe/Moscow,09:00,18:00,Mon;Tue;Wed;Thu;Fri,hybrid,2026-05-01\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)
    rows = data_loader.load_dataset("employees")

    assert rows[0]["id"] == 1
    assert rows[0]["work_days"] == ["Mon", "Tue", "Wed", "Thu", "Fri"]


def test_csv_loader_raises_on_invalid_data(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv_path = data_dir / "employees.csv"
    csv_path.write_text("id,name\n1,Broken\n", encoding="utf-8")

    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)

    with pytest.raises(ValueError):
        data_loader.load_dataset("employees")


def test_json_is_used_when_csv_absent(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    json_path = data_dir / "absences.json"
    json_path.write_text(
        '[{"id": 1, "employee_id": 1, "type": "отпуск", "start_date": "2026-05-20", "end_date": "2026-05-21"}]',
        encoding="utf-8",
    )

    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)
    rows = data_loader.load_dataset("absences", required=False)

    assert rows[0]["type"] == "отпуск"


def test_upload_validation_keeps_existing_json_when_bad_upload_fails(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    json_path = data_dir / "employees.json"
    json_path.write_text(
        '[{"id": 1, "name": "Анна", "team": "People", "role": "HR", "timezone": "Europe/Moscow", "work_start": "09:00", "work_end": "18:00", "work_days": ["Mon"], "work_format": "hybrid", "last_update_date": "2026-05-01"}]',
        encoding="utf-8",
    )

    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)

    with pytest.raises(ValueError):
        data_loader.save_uploaded_table("employees", ".csv", b"id,name\n1,Broken\n")

    assert json_path.exists()
