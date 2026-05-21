import styles from './StreakBadge.module.css'

function CrownIcon() {
  return (
    <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="var(--accent)" stroke="none">
      <path d="M2 19h20l-2-10-5 5-3-7-3 7-5-5-2 10z" />
    </svg>
  )
}

export default function StreakBadge({ streak }) {
  if (!streak) return null

  return (
    <div className={styles.badge} aria-label={`${streak} day streak${streak >= 3 ? ', on a roll!' : ''}`}>
      {streak >= 3 && <CrownIcon />}
      <span className={styles.count} aria-hidden="true">{streak}</span>
      <span className={styles.label} aria-hidden="true">streak</span>
    </div>
  )
}
