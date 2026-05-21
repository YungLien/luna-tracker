import styles from './Login.module.css'
import lunaImg from '../assets/luna/cat_sit_still.png'
import morningScene from '../assets/scenes/morning.png'

export default function Login() {
  const base = import.meta.env.VITE_API_BASE_URL || ''
  const authUrl = `${base}/auth/strava`

  return (
    <div className={styles.page} style={{ backgroundImage: `url(${morningScene})` }}>
      <img src={lunaImg} alt="Luna" className={styles.luna} />
      <div className={styles.overlay} />
      <div className={styles.content}>
        <h1 className={styles.title}>Luna Tracker</h1>
        <p className={styles.tagline}>用 Luna 陪你好好生活</p>
        <a href={authUrl} className={styles.stravaBtn}>
          Connect with Strava
        </a>
      </div>
    </div>
  )
}
