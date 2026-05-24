from __future__ import annotations
import csv, json, os, re, uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Type
from pydantic import BaseModel, ValidationError
from app.models import Absence, Employee, Event, HRProfile, ScheduleConfirmation, Task

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / 'data' / 'synthetic'
FALLBACK_DATA_DIR = BACKEND_DIR / 'data'
DATA_DIR = Path(os.getenv('WORKTIME_DATA_DIR', DEFAULT_DATA_DIR)).resolve()
DATASET_ORDER = ['employees','events','hr_profiles','absences','tasks','schedule_confirmations']
ALLOWED_DATASETS = set(DATASET_ORDER)
ALLOWED_SUFFIXES = {'.json','.csv'}
REQUIRED_COLUMNS = {
 'employees':['id','name','team','role','timezone','work_start','work_end','work_days','work_format','last_update_date'],
 'events':['id','employee_id','title','start_datetime','end_datetime','source','type'],
 'hr_profiles':['employee_id','hr_timezone','hr_work_format','hr_work_start','hr_work_end'],
 'absences':['id','employee_id','type','start_date','end_date'],
 'tasks':['id','employee_id','created_by_user_id','created_by_role','department','type','title','description','due_date','status','employee_comment','created_at','updated_at'],
 'schedule_confirmations':['employee_id','confirmed_by_user_id','confirmed_at','comment','status','updated_at'],
}
MODEL_BY_DATASET={'employees':Employee,'events':Event,'hr_profiles':HRProfile,'absences':Absence,'tasks':Task,'schedule_confirmations':ScheduleConfirmation}

def _display_path(path):
    if path is None: return None
    try: return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace('\\','/')
    except ValueError: return str(path.resolve())
def _target_data_dir(): return Path(os.getenv('WORKTIME_DATA_DIR', DATA_DIR)).resolve()
def _normalize_identifier(value):
    if isinstance(value,int): return value
    text=str(value).strip()
    if text.isdigit(): return int(text)
    m=re.search(r'(\d+)$', text)
    if m: return int(m.group(1))
    raise ValueError(f'Некорректный идентификатор: {value}')
def _normalize_datetime(value):
    if not isinstance(value,str) or 'T' not in value: return value
    try: return datetime.fromisoformat(value.strip()).replace(tzinfo=None).isoformat(timespec='seconds')
    except ValueError: return value
def _convert_csv_value(value):
    if value is None: return value
    text=value.strip()
    if not text: return text
    if ';' in text: return [i.strip() for i in text.split(';') if i.strip()]
    if '|' in text: return [i.strip() for i in text.split('|') if i.strip()]
    if text.isdigit(): return int(text)
    return text
def _normalize_row(dataset,row):
    n=dict(row)
    if dataset=='employees':
        n['id']=_normalize_identifier(n['id'])
        if isinstance(n.get('work_days'),str): n['work_days']=_convert_csv_value(n['work_days'])
    elif dataset=='events':
        n['id']=_normalize_identifier(n['id']); n['employee_id']=_normalize_identifier(n['employee_id']); n['start_datetime']=_normalize_datetime(n['start_datetime']); n['end_datetime']=_normalize_datetime(n['end_datetime'])
    elif dataset in {'hr_profiles','schedule_confirmations'}:
        n['employee_id']=_normalize_identifier(n['employee_id'])
    elif dataset=='absences':
        n['id']=_normalize_identifier(n['id']); n['employee_id']=_normalize_identifier(n['employee_id'])
    elif dataset=='tasks':
        n['id']=_normalize_identifier(n['id']); n['employee_id']=_normalize_identifier(n['employee_id'])
        if n.get('related_event_id') not in (None,''): n['related_event_id']=_normalize_identifier(n['related_event_id'])
    return n
def _validate_columns(dataset, rows, filename):
    if not rows: return
    missing=sorted(set(REQUIRED_COLUMNS.get(dataset,[]))-set(rows[0].keys()))
    if missing: raise ValueError(f"В {filename} отсутствуют обязательные колонки: {', '.join(missing)}")
def _validate_rows(dataset, rows, filename=''):
    model=MODEL_BY_DATASET.get(dataset)
    if not model: return rows
    _validate_columns(dataset, rows, filename or dataset)
    out=[]; errors=[]
    for i,row in enumerate(rows,1):
        try: out.append(model(**_normalize_row(dataset,row)).model_dump())
        except (ValidationError,ValueError,KeyError) as e: errors.append(f'row {i}: {e.errors() if isinstance(e,ValidationError) else str(e)}')
    if errors: raise ValueError(f"Некорректные данные в {dataset}: {'; '.join(errors[:3])}")
    return out
def _active_data_dirs():
    if os.getenv('WORKTIME_DATA_DIR'): return [Path(os.getenv('WORKTIME_DATA_DIR')).resolve()]
    dirs=[DATA_DIR]; fb=FALLBACK_DATA_DIR.resolve()
    if fb not in dirs: dirs.append(fb)
    return dirs
def _read_table(path):
    if path.suffix=='.json': rows=json.loads(path.read_text(encoding='utf-8'))
    elif path.suffix=='.csv':
        with path.open('r',encoding='utf-8-sig',newline='') as f: rows=[{k:_convert_csv_value(v) for k,v in r.items()} for r in csv.DictReader(f)]
    else: raise ValueError('Поддерживаются только .json и .csv файлы')
    if not isinstance(rows,list): raise ValueError(f'Файл {path.name} должен содержать список объектов')
    return rows
def load_table(filename, required=True, validate_as=None, data_dir=None):
    for directory in ([data_dir] if data_dir else _active_data_dirs()):
        path=Path(directory)/filename
        if path.exists():
            rows=_read_table(path)
            return _validate_rows(validate_as, rows, path.name) if validate_as else rows
    if required: raise FileNotFoundError(f"Файл не найден. Проверенные пути: {', '.join(str(Path(d)/filename) for d in ([data_dir] if data_dir else _active_data_dirs()))}")
    return []
def _dataset_path_in_dir(dataset,directory):
    csv_path=directory/f'{dataset}.csv'; json_path=directory/f'{dataset}.json'
    return csv_path if csv_path.exists() else (json_path if json_path.exists() else None)
def get_dataset_path(dataset):
    for d in _active_data_dirs():
        p=_dataset_path_in_dir(dataset,Path(d))
        if p: return p
    return None
def get_data_source_info():
    datasets={ds:get_dataset_path(ds) for ds in DATASET_ORDER}; active=[p for p in datasets.values() if p]
    source=active[0].parent if active else _active_data_dirs()[0]
    return {'active_source':_display_path(source),'fallback_source':_display_path(FALLBACK_DATA_DIR),'env_override':bool(os.getenv('WORKTIME_DATA_DIR')),'priority':[_display_path(d) for d in _active_data_dirs()],'datasets':{k:_display_path(v) for k,v in datasets.items()}}
def get_schema_definitions(): return REQUIRED_COLUMNS
def load_dataset(dataset, required=True):
    for d in _active_data_dirs():
        p=_dataset_path_in_dir(dataset,Path(d))
        if p: return load_table(p.name, required=required, validate_as=dataset, data_dir=Path(d))
    if required: raise FileNotFoundError(f'Файл {dataset}.csv/json не найден')
    return []
def _write_csv(path, dataset, rows):
    fieldnames=list(REQUIRED_COLUMNS[dataset])
    for row in rows:
        for key in row:
            if key not in fieldnames: fieldnames.append(key)
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f, fieldnames=fieldnames); writer.writeheader()
        for row in rows:
            prepared=dict(row)
            for k,v in list(prepared.items()):
                if isinstance(v, list): prepared[k]='|'.join(str(i) for i in v)
                elif isinstance(v, dict): prepared[k]=json.dumps(v,ensure_ascii=False)
            writer.writerow(prepared)
def _safe_write_dataset(dataset, rows, preferred_suffix=None):
    if dataset not in ALLOWED_DATASETS: raise ValueError('Неизвестный набор данных')
    current=get_dataset_path(dataset); target=current.parent if current else _target_data_dir(); target.mkdir(parents=True, exist_ok=True)
    suffix=preferred_suffix or (current.suffix if current else '.json')
    final=target/f'{dataset}{suffix}'; tmp=target/f'.{dataset}.save-{uuid.uuid4().hex}{suffix}'
    if suffix=='.json': tmp.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    elif suffix=='.csv': _write_csv(tmp, dataset, rows)
    else: raise ValueError('Поддерживаются только .json и .csv файлы')
    try: load_table(tmp.name, validate_as=dataset, data_dir=target)
    except Exception: tmp.unlink(missing_ok=True); raise
    tmp.replace(final); return final
def _safe_write_json_dataset(dataset, rows): return _safe_write_dataset(dataset, rows, preferred_suffix='.json')
def save_uploaded_table(dataset, suffix, content):
    if dataset not in ALLOWED_DATASETS: raise ValueError('Неизвестный набор данных')
    if suffix not in ALLOWED_SUFFIXES: raise ValueError('Можно загружать только JSON или CSV')
    target=_target_data_dir(); target.mkdir(parents=True, exist_ok=True); final=target/f'{dataset}{suffix}'; tmp=target/f'.{dataset}.upload-{uuid.uuid4().hex}{suffix}'
    tmp.write_bytes(content)
    try: load_table(tmp.name, validate_as=dataset, data_dir=target)
    except Exception: tmp.unlink(missing_ok=True); raise
    tmp.replace(final); alt=target/f"{dataset}{'.json' if suffix=='.csv' else '.csv'}"; alt.unlink(missing_ok=True); return final

def load_employees(): return load_dataset('employees')
def load_events(): return load_dataset('events')
def save_events(events): return _safe_write_dataset('events', events)
def load_hr_profiles(): return load_dataset('hr_profiles')
def load_absences(): return load_dataset('absences', required=False)
def load_tasks(): return load_dataset('tasks', required=False)
def save_tasks(tasks): return _safe_write_json_dataset('tasks', tasks)
def load_schedule_confirmations(): return load_dataset('schedule_confirmations', required=False)
def save_schedule_confirmations(items): return _safe_write_json_dataset('schedule_confirmations', items)
