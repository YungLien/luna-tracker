import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client'
import { MEAL_LABELS, mealLabelPlural } from '../constants/mealLabels'
import { formatKm } from '../utils/formatKm'
import styles from './Weekly.module.css'

const MEAL_COLORS = {
  breakfast: '#e8a87c',
  lunch: '#8aaa7a',
  dinner: '#c9a88a',
  snack: '#b8a0c8',
}

const CORE_MEALS = ['breakfast', 'lunch', 'dinner']

function localDateStr(d) {
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, '0'),
    String(d.getDate()).padStart(2, '0'),
  ].join('-')
}

function getWeekMonday() {
  const today = new Date()
  const dow = today.getDay()
  const daysSinceMon = dow === 0 ? 6 : dow - 1
  const monday = new Date(today)
  monday.setDate(today.getDate() - daysSinceMon)
  return monday
}

function formatDayLabel(dateStr) {
  const d = new Date(dateStr + 'T12:00:00')
  const today = localDateStr(new Date())
  if (dateStr === today) return 'Today'
  return d.toLocaleDateString('en-AU', { weekday: 'long', month: 'short', day: 'numeric' })
}

function buildWeekDays(meals) {
  const todayStr = localDateStr(new Date())
  const monday = getWeekMonday()

  const dates = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    return localDateStr(d)
  })

  const mealsByDate = {}
  for (const meal of meals) {
    if (!mealsByDate[meal.date]) mealsByDate[meal.date] = {}
    mealsByDate[meal.date][meal.meal_type] = meal
  }

  return dates.map(dateStr => ({
    dateStr,
    label: formatDayLabel(dateStr),
    meals: mealsByDate[dateStr] || {},
    isFuture: dateStr > todayStr,
  }))
}

function buildInsights(weekDays) {
  const pastDays = weekDays.filter(d => !d.isFuture)
  if (!pastDays.length) return []

  const avgByType = CORE_MEALS.map(type => {
    const scores = pastDays.map(d => d.meals[type]?.health_score ?? 0)
    return {
      type,
      avg: scores.reduce((a, b) => a + b, 0) / scores.length,
    }
  })

  const allScores = pastDays.flatMap(d => CORE_MEALS.map(t => d.meals[t]?.health_score ?? 0))
  const overallAvg = allScores.reduce((a, b) => a + b, 0) / allScores.length

  const insights = []

  const lowest = [...avgByType].sort((a, b) => a.avg - b.avg)[0]
  if (lowest && lowest.avg < 6) {
    insights.push(`Your ${mealLabelPlural(lowest.type)} average ${lowest.avg.toFixed(1)}/10 — a good place to start improving.`)
  }

  if (overallAvg >= 7.5) {
    insights.push(`Great week overall — averaging ${overallAvg.toFixed(1)}/10 across all meals.`)
  } else if (overallAvg >= 5) {
    insights.push(`Solid week — averaging ${overallAvg.toFixed(1)}/10. A few tweaks could push you higher.`)
  }

  const missedCount = pastDays.reduce((sum, d) =>
    sum + CORE_MEALS.filter(t => !d.meals[t]).length, 0)
  if (missedCount >= 3) {
    insights.push(`${missedCount} meals were not logged — unlogged meals count as 0 points.`)
  }

  return insights
}

export default function Weekly() {
  const [meals, setMeals] = useState(null)
  const [activities, setActivities] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    client.get('/api/meals/history?days=7').then(r => setMeals(r.data))
    client.post('/api/activities/sync?days=7')
      .catch(() => {})
      .finally(() => {
        client.get('/api/activities/history?days=7').then(r => setActivities(r.data))
      })
  }, [])

  const loading = meals === null || activities === null
  if (loading) return (
    <div className={styles.loading} role="status" aria-label="Loading weekly summary…">
      <div className={styles.loadingDot} />
    </div>
  )

  const mondayStr = localDateStr(getWeekMonday())

  const weeklyKm = activities
    .filter(a => a.activity_type === 'Run' && a.date >= mondayStr)
    .reduce((sum, a) => sum + (a.distance_km || 0), 0)

  const weekDays = buildWeekDays(meals)
  const insights = buildInsights(weekDays)

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <button className={styles.back} onClick={() => navigate('/')}>← Back</button>
        <span className={styles.title}>This Week</span>
      </div>

      {weeklyKm > 0 && (
        <div className={styles.runCard}>
          <span className={styles.runLabel}>Running this week</span>
          <span className={styles.km}>{formatKm(weeklyKm)} km</span>
        </div>
      )}

      <div className={styles.section}>
        {weekDays.map(({ dateStr, label, meals: dayMeals, isFuture }) => {
          const dayScore = CORE_MEALS.reduce((sum, t) => sum + (dayMeals[t]?.health_score ?? 0), 0)
          const hasSnack = !!dayMeals.snack

          return (
            <div key={dateStr} className={`${styles.dayCard} ${isFuture ? styles.dayFuture : ''}`}>
              <div className={styles.dayHeader}>
                <span className={styles.dayLabel}>{label}</span>
                {isFuture
                  ? <span className={styles.dayUpcoming}>upcoming</span>
                  : <span className={styles.dayTotal}>{dayScore}/30</span>
                }
              </div>

              {!isFuture && (
                <div className={styles.mealList}>
                  {CORE_MEALS.map(type => {
                    const meal = dayMeals[type]
                    const score = meal?.health_score ?? 0
                    const isLogged = !!meal
                    const isHigh = score >= 8
                    const isLow = !isLogged || score <= 4
                    return (
                      <div key={type} className={styles.mealRow}>
                        <span
                          className={styles.mealTag}
                          style={{
                            background: MEAL_COLORS[type] + (isLogged ? '33' : '18'),
                            color: isLogged ? MEAL_COLORS[type] : '#aaa',
                          }}
                        >
                          {MEAL_LABELS[type]}
                        </span>
                        <span className={`${styles.mealDesc} ${!isLogged ? styles.mealDescEmpty : ''}`}>
                          {isLogged ? meal.description : 'Not logged'}
                        </span>
                        <span className={`${styles.mealScore} ${isHigh ? styles.scoreHigh : isLow ? styles.scoreLow : styles.scoreMid}`}>
                          {score}/10
                        </span>
                      </div>
                    )
                  })}

                  {hasSnack && (
                    <div className={styles.mealRow}>
                      <span
                        className={styles.mealTag}
                        style={{ background: MEAL_COLORS.snack + '33', color: MEAL_COLORS.snack }}
                      >
                        {MEAL_LABELS.snack}
                      </span>
                      <span className={styles.mealDesc}>{dayMeals.snack.description}</span>
                      <span className={`${styles.mealScore} ${styles.scoreSnack}`}>
                        {dayMeals.snack.health_score}/10
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {insights.length > 0 && (
        <div className={styles.insightCard}>
          <p className={styles.insightTitle}>Where to improve</p>
          {insights.map((text, i) => (
            <p key={i} className={styles.insightText}>· {text}</p>
          ))}
        </div>
      )}
    </div>
  )
}
