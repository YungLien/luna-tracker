import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import client from '../api/client'
import useLunaState from '../hooks/useLunaState'
import LunaScene from '../components/LunaScene/LunaScene'
import MealCard from '../components/MealCard/MealCard'
import RunCard from '../components/RunCard/RunCard'
import StreakBadge from '../components/StreakBadge/StreakBadge'
import WeeklySheet from '../components/WeeklySheet/WeeklySheet'
import styles from './Dashboard.module.css'

const MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'snack']
const VALID_SCENES = ['morning', 'afternoon', 'night']
const SCENE_DEFAULT_POSE = {
  morning:   'cat_sit_still',
  afternoon: 'cat_chilling',
  night:     'sleepy_cat',
}

/** Dev / layout preview — must match backend `pose` strings & `POSE_MAP` in useLunaState */
const VALID_PREVIEW_POSES = [
  'cat_sit_still',
  'cat_chilling',
  'cat_stretch',
  'sleepy_cat',
  'cat_tickling',
  'unhappy_cat',
  'playful_cat',
  'cat_in_shocked',
  'cat_one_leg_up',
]

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [weeklyOpen, setWeeklyOpen] = useState(false)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const sceneOverride = VALID_SCENES.includes(searchParams.get('scene'))
    ? searchParams.get('scene')
    : null

  const poseParam = searchParams.get('pose')
  const poseOverride = VALID_PREVIEW_POSES.includes(poseParam) ? poseParam : null

  const lunaWithOverride = data?.luna
    ? {
        ...data.luna,
        ...(sceneOverride && {
          scene: sceneOverride,
          pose: poseOverride ?? SCENE_DEFAULT_POSE[sceneOverride],
        }),
        ...(!sceneOverride && poseOverride && { pose: poseOverride }),
      }
    : data?.luna

  const { sceneImg } = useLunaState(lunaWithOverride)

  const fetchDashboard = useCallback(async (firstOpen = false) => {
    try {
      const res = await client.get(`/api/dashboard/today${firstOpen ? '?first_open=true' : ''}`)
      setData(res.data)
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token')
        navigate('/login', { replace: true })
      }
    }
  }, [navigate])

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10)
    const lastOpen = localStorage.getItem('luna_last_open')
    const isFirstOpen = lastOpen !== today
    if (isFirstOpen) localStorage.setItem('luna_last_open', today)

    fetchDashboard(isFirstOpen)
    client.post('/api/activities/sync?days=2')
      .then(() => fetchDashboard(false))
      .catch(() => {})
  }, [fetchDashboard])

  // Drop streak-celebration pose after 3 s
  useEffect(() => {
    if (!data?.luna?.streak_celebrate) return
    const t = setTimeout(() => fetchDashboard(false), 3000)
    return () => clearTimeout(t)
  }, [data?.luna?.streak_celebrate, fetchDashboard])

  if (!data) {
    return (
      <div className={styles.loading} role="status" aria-label="Loading Luna…">
        <div className={styles.loadingDot} />
      </div>
    )
  }

  const { user, meals, activity, luna, streak } = data
  const hasAnyMeal = Object.values(meals).some(m => m !== null)

  return (
    <div className={styles.page} style={{ backgroundImage: `url(${sceneImg})` }}>
      <LunaScene luna={lunaWithOverride} hasAnyMeal={hasAnyMeal} />

      <div className={styles.overlay} />

      <div className={styles.content}>
        <div className={styles.topRow}>
          <span className={styles.greeting}>
            {user?.name ? `Hi, ${user.name.split(' ')[0]}` : 'Hello'}
          </span>
          <div className={styles.topRight}>
            <button className={styles.weeklyLink} onClick={() => setWeeklyOpen(true)}>This week</button>
            <StreakBadge streak={streak} />
          </div>
        </div>

        <div className={styles.meals}>
          {MEAL_TYPES.map(type => (
            <MealCard
              key={type}
              mealType={type}
              meal={meals[type]}
              onLogged={fetchDashboard}
            />
          ))}
        </div>

        <RunCard activity={activity} />
      </div>

      <WeeklySheet open={weeklyOpen} onClose={() => setWeeklyOpen(false)} />
    </div>
  )
}
