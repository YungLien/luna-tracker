import styles from './LunaScene.module.css'
import useLunaState from '../../hooks/useLunaState'

/** Run pose (`playful_cat`) needs its own anchor per scene — not only afternoon. */
const PLAYFUL_SCENE = {
  morning: styles.morningPlayful,
  afternoon: styles.afternoonPlayful,
  night: styles.nightPlayful,
}

/** Healthy-meal pose (`cat_tickling`): same slot as base scene, slightly higher `top`. */
const TICKLING_ADJUST = {
  morning: styles.morningTickling,
  afternoon: styles.afternoonTickling,
  night: styles.nightTickling,
}

export default function LunaScene({ luna, hasAnyMeal }) {
  const { poseImg } = useLunaState(luna)
  const isPlayful = luna?.pose === 'playful_cat'
  const isTickling = luna?.pose === 'cat_tickling'
  const baseScene = styles[luna?.scene] ?? ''
  const ticklingAdjust =
    isTickling && luna?.scene && TICKLING_ADJUST[luna.scene] ? TICKLING_ADJUST[luna.scene] : ''
  const nightUnhappy =
    luna?.pose === 'unhappy_cat' && luna?.scene === 'night' ? styles.nightUnhappy : ''

  const sceneClass =
    isPlayful && luna?.scene && PLAYFUL_SCENE[luna.scene]
      ? PLAYFUL_SCENE[luna.scene]
      : [baseScene, ticklingAdjust, nightUnhappy].filter(Boolean).join(' ')
  const emptyClass = !hasAnyMeal ? styles.empty : ''
  const playfulClass = isPlayful ? styles.playful : ''
  return <img src={poseImg} alt="Luna" className={`${styles.luna} ${sceneClass} ${emptyClass} ${playfulClass}`} />
}
