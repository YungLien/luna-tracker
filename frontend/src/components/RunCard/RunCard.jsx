import styles from './RunCard.module.css'
import runIcon from '../../assets/run_icon.png'
import { formatKm } from '../../utils/formatKm'

function formatDuration(sec) {
  if (sec == null) return null
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

export default function RunCard({ activity }) {
  if (!activity?.has_run) return null

  return (
    <div className={styles.card}>
      <img src={runIcon} alt="" aria-hidden="true" className={styles.icon} />
      <div className={styles.info}>
        <span className={styles.distance}>{formatKm(activity.distance_km)} km</span>
        <span className={styles.detail}>{formatDuration(activity.duration_min)} · {activity.pace}</span>
      </div>
    </div>
  )
}
