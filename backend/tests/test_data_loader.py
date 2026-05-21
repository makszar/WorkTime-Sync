import pytest

from app import data_loader


def test_root_synthetic_data_dir_has_priority(monkeypatch, tmp_path):
    root_synthetic = tmp_path / "data" / "synthetic"
    fallback = tmp_path / "backend" / "data"
    root_synthetic.mkdir(parents=True)
    fallback.mkdir(parents=True)

    (root_synthetic / "employees.json").write_text(
        """[
          {
            "id": 1,
            "name": "Root User",
            "team": "People",
            "role": "HR",
            "timezone": "Europe/Moscow",
            "work_start": "09:00",
            "work_end": "18:00",
            "work_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "work_format": "hybrid",
            "last_update_date": "2026-05-01"
          }
        ]""",
        encoding="utf-8",
    )
    (fallback / "employees.json").write_text(
        """[
          {
            "id": 2,
            "name": "Fallback User",
            "team": "Backend",
            "role": "Developer",
            "timezone": "Europe/Moscow",
            "work_start": "10:00",
            "work_end": "19:00",
            "work_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "work_format": "remote",
            "last_update_date": "2026-05-01"
          }
        ]""",
        encoding="utf-8",
    )

    monkeypatch.delenv("WORKTIME_DATA_DIR", raising=False)
    monkeypatch.setattr(data_loader, "DATA_DIR", root_synthetic)
    monkeypatch.setattr(data_loader, "FALLBACK_DATA_DIR", fallback)

    rows = data_loader.load_dataset("employees")

    assert rows[0]["name"] == "Root User"


def test_fallback_backend_data_is_used_when_root_missing(monkeypatch, tmp_path):
    root_synthetic = tmp_path / "data" / "synthetic"
    fallback = tmp_path / "backend" / "data"
    root_synthetic.mkdir(parents=True)
    fallback.mkdir(parents=True)

    (fallback / "absences.json").write_text(
        '[{"id": 1, "employee_id": 1, "type": "отпуск", "start_date": "2026-05-20", "end_date": "2026-05-21"}]',
        encoding="utf-8",
    )

    monkeypatch.delenv("WORKTIME_DATA_DIR", raising=False)
    monkeypatch.setattr(data_loader, "DATA_DIR", root_synthetic)
    monkeypatch.setattr(data_loader, "FALLBACK_DATA_DIR", fallback)

    rows = data_loader.load_dataset("absences", required=False)

    assert rows[0]["type"] == "отпуск"


def test_env_data_dir_override(monkeypatch, tmp_path):
    custom_dir = tmp_path / "custom_data"
    custom_dir.mkdir()

    (custom_dir / "employees.csv").write_text(
        "id,name,team,role,timezone,work_start,work_end,work_days,work_format,last_update_date\n"
        "emp001,Анна,People,HR,Europe/Moscow,09:00,18:00,Mon|Tue|Wed|Thu|Fri,hybrid,2026-05-01\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("WORKTIME_DATA_DIR", str(custom_dir))

    rows = data_loader.load_dataset("employees")

    assert rows[0]["id"] == 1
    assert rows[0]["work_days"] == ["Mon", "Tue", "Wed", "Thu", "Fri"]


def test_synthetic_csv_string_ids_are_normalized(monkeypatch, tmp_path):
    data_dir = tmp_path / "data" / "synthetic"
    data_dir.mkdir(parents=True)

    (data_dir / "employees.csv").write_text(
        "id,name,team,role,timezone,work_start,work_end,work_days,work_format,last_update_date\n"
        "emp010,Тимур,Product,PM,Europe/Moscow,09:00,18:00,Mon|Tue|Wed|Thu|Fri,hybrid,2026-05-14\n",
        encoding="utf-8",
    )
    (data_dir / "events.csv").write_text(
        "id,employee_id,title,start_datetime,end_datetime,source,type\n"
        "evt011,emp010,Demo,2026-05-20T10:00:00+03:00,2026-05-20T11:00:00+03:00,google_calendar,meeting\n",
        encoding="utf-8",
    )
    (data_dir / "absences.csv").write_text(
        "id,employee_id,type,start_date,end_date\n"
        "abs002,emp010,vacation,2026-05-21,2026-05-22\n",
        encoding="utf-8",
    )

    monkeypatch.delenv("WORKTIME_DATA_DIR", raising=False)
    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)
    monkeypatch.setattr(data_loader, "FALLBACK_DATA_DIR", tmp_path / "missing")

    employees = data_loader.load_dataset("employees")
    events = data_loader.load_dataset("events")
    absences = data_loader.load_dataset("absences")

    assert employees[0]["id"] == 10
    assert employees[0]["work_days"] == ["Mon", "Tue", "Wed", "Thu", "Fri"]
    assert events[0]["id"] == 11
    assert events[0]["employee_id"] == 10
    assert events[0]["start_datetime"] == "2026-05-20T10:00:00"
    assert absences[0]["id"] == 2
    assert absences[0]["employee_id"] == 10


def test_csv_loader_raises_on_invalid_data(monkeypatch, tmp_path):
    data_dir = tmp_path / "data" / "synthetic"
    data_dir.mkdir(parents=True)
    csv_path = data_dir / "employees.csv"
    csv_path.write_text("id,name\nbad,Broken\n", encoding="utf-8")

    monkeypatch.delenv("WORKTIME_DATA_DIR", raising=False)
    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)
    monkeypatch.setattr(data_loader, "FALLBACK_DATA_DIR", tmp_path / "missing")

    with pytest.raises(ValueError):
        data_loader.load_dataset("employees")


def test_upload_saves_to_root_synthetic_and_removes_alternate(monkeypatch, tmp_path):
    data_dir = tmp_path / "data" / "synthetic"
    data_dir.mkdir(parents=True)
    (data_dir / "absences.json").write_text(
        '[{"id": 1, "employee_id": 1, "type": "отпуск", "start_date": "2026-05-20", "end_date": "2026-05-21"}]',
        encoding="utf-8",
    )

    monkeypatch.delenv("WORKTIME_DATA_DIR", raising=False)
    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)
    monkeypatch.setattr(data_loader, "FALLBACK_DATA_DIR", tmp_path / "backend" / "data")

    saved_path = data_loader.save_uploaded_table(
        "absences",
        ".csv",
        b"id,employee_id,type,start_date,end_date\nabs002,emp002,komandirovka,2026-05-22,2026-05-23\n",
    )

    assert saved_path == data_dir / "absences.csv"
    assert saved_path.exists()
    assert not (data_dir / "absences.json").exists()


def test_invalid_upload_keeps_existing_file(monkeypatch, tmp_path):
    data_dir = tmp_path / "data" / "synthetic"
    data_dir.mkdir(parents=True)
    employees_path = data_dir / "employees.csv"
    original_content = (
        "id,name,team,role,timezone,work_start,work_end,work_days,work_format,last_update_date\n"
        "emp001,Анна,People,HR,Europe/Moscow,09:00,18:00,Mon|Tue|Wed|Thu|Fri,hybrid,2026-05-01\n"
    )
    employees_path.write_text(original_content, encoding="utf-8")

    monkeypatch.delenv("WORKTIME_DATA_DIR", raising=False)
    monkeypatch.setattr(data_loader, "DATA_DIR", data_dir)
    monkeypatch.setattr(data_loader, "FALLBACK_DATA_DIR", tmp_path / "backend" / "data")

    with pytest.raises(ValueError):
        data_loader.save_uploaded_table("employees", ".csv", b"id,name\nbad,Broken\n")

    assert employees_path.read_text(encoding="utf-8") == original_content
