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
        "1,Анна,People,HR,Europe/Moscow,09:00,18:00,Mon;Tue;Wed;Thu;Fri,hybrid,2026-05-01\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("WORKTIME_DATA_DIR", str(custom_dir))

    rows = data_loader.load_dataset("employees")

    assert rows[0]["id"] == 1
    assert rows[0]["work_days"] == ["Mon", "Tue", "Wed", "Thu", "Fri"]


def test_csv_loader_raises_on_invalid_data(monkeypatch, tmp_path):
    data_dir = tmp_path / "data" / "synthetic"
    data_dir.mkdir(parents=True)
    csv_path = data_dir / "employees.csv"
    csv_path.write_text("id,name\n1,Broken\n", encoding="utf-8")

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
        b"id,employee_id,type,start_date,end_date\n2,2,komandirovka,2026-05-22,2026-05-23\n",
    )

    assert saved_path == data_dir / "absences.csv"
    assert saved_path.exists()
    assert not (data_dir / "absences.json").exists()
