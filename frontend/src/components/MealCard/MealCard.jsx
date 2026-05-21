import { useState } from 'react'
import styles from './MealCard.module.css'
import client from '../../api/client'
import { MEAL_LABELS } from '../../constants/mealLabels'

export default function MealCard({ mealType, meal, onLogged }) {
  const [editing, setEditing]         = useState(false)
  const [description, setDescription] = useState('')
  const [score, setScore]             = useState(7)
  const [saving, setSaving]           = useState(false)

  function openForm() {
    setDescription(meal?.description || '')
    setScore(meal?.health_score ?? 7)
    setEditing(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await client.post('/api/meals', { meal_type: mealType, description, health_score: score })
      setEditing(false)
      onLogged()
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!meal?.id) return
    setSaving(true)
    try {
      await client.delete(`/api/meals/${meal.id}`)
      setEditing(false)
      onLogged()
    } finally {
      setSaving(false)
    }
  }

  const isLogged = !!meal && !editing

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.label}>{MEAL_LABELS[mealType]}</span>
        {!editing && (
          <button className={isLogged ? styles.editBtn : styles.logBtn} onClick={openForm}>
            {isLogged ? 'Edit' : 'Add'}
          </button>
        )}
      </div>

      {isLogged && (
        <div className={styles.logged}>
          <span className={styles.desc}>{meal.description}</span>
          <span className={`${styles.score} ${meal.is_healthy ? styles.healthy : styles.neutral}`}>
            {meal.health_score}/10
          </span>
        </div>
      )}

      {editing && (
        <form onSubmit={handleSubmit} className={styles.form}>
          <label className={styles.inputLabel} htmlFor={`meal-desc-${mealType}`}>
            What did you eat?
          </label>
          <input
            id={`meal-desc-${mealType}`}
            className={styles.input}
            type="text"
            placeholder="e.g. oatmeal, bubble tea…"
            value={description}
            onChange={e => setDescription(e.target.value)}
            required
            autoFocus
          />
          <div className={styles.sliderRow}>
            <label className={styles.sliderLabel} htmlFor={`meal-score-${mealType}`}>
              Health score: <strong>{score}</strong>/10
            </label>
            <input
              id={`meal-score-${mealType}`}
              type="range" min="0" max="10" value={score}
              aria-valuenow={score}
              aria-valuemin={0}
              aria-valuemax={10}
              aria-label={`Health score: ${score} out of 10`}
              onChange={e => setScore(Number(e.target.value))}
              className={styles.slider}
            />
          </div>
          <div className={styles.actions}>
            {meal?.id && (
              <button
                type="button"
                className={styles.deleteBtn}
                onClick={handleDelete}
                disabled={saving}
                aria-label={`Delete ${MEAL_LABELS[mealType]} entry`}
              >
                Delete
              </button>
            )}
            <div className={styles.actionsRight}>
              <button type="button" className={styles.cancelBtn} onClick={() => setEditing(false)}>Cancel</button>
              <button type="submit" className={styles.saveBtn} disabled={saving} aria-busy={saving}>
                {saving ? '…' : 'Save'}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  )
}
