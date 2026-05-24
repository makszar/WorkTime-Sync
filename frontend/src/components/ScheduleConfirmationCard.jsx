const LABELS = {
  confirmed: 'График подтверждён',
  pending: 'Ожидает подтверждения',
  rejected: 'Отклонено',
  change_requested: 'Запрошено изменение',
  not_confirmed: 'Нет подтверждения'
};

export default function ScheduleConfirmationCard({ status, comment, onConfirm, canConfirm = false }) {
  return (
    <article className="panel scheduleCard">
      <div className="panelHeader">
        <div>
          <h2>Подтверждение графика</h2>
          <p>{LABELS[status] || status}</p>
        </div>
        <span className={`statusBadge ${status === 'confirmed' ? 'low' : 'medium'}`}>{LABELS[status] || status}</span>
      </div>
      {comment && <p className="noteText">{comment}</p>}
      {canConfirm && <button className="primaryButton iconTextButton" type="button" onClick={onConfirm}><img src="/icons/save.svg" alt="" /><span>Подтвердить график</span></button>}
    </article>
  );
}
