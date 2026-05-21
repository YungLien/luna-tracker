import catSitStill   from '../assets/luna/cat_sit_still.png'
import catChilling   from '../assets/luna/cat_chilling.png'
import catStretch    from '../assets/luna/cat_stretch.png'
import sleepyCat     from '../assets/luna/sleepy_cat.png'
import catTickling   from '../assets/luna/cat_tickling.png'
import unhappyCat    from '../assets/luna/unhappy_cat.png'
import playfulCat    from '../assets/luna/playful_cat.png'
import catInShocked  from '../assets/luna/cat_in_shocked.png'
import catOneLegUp   from '../assets/luna/cat_one_leg_up.png'
import morningScene  from '../assets/scenes/morning.png'
import afternoonScene from '../assets/scenes/afternoon.png'
import nightScene    from '../assets/scenes/night.png'

const POSE_MAP = {
  cat_sit_still:  catSitStill,
  cat_chilling:   catChilling,
  cat_stretch:    catStretch,
  sleepy_cat:     sleepyCat,
  cat_tickling:   catTickling,
  unhappy_cat:    unhappyCat,
  playful_cat:    playfulCat,
  cat_in_shocked: catInShocked,
  cat_one_leg_up: catOneLegUp,
}

const SCENE_MAP = {
  morning:   morningScene,
  afternoon: afternoonScene,
  night:     nightScene,
}

export default function useLunaState(luna) {
  return {
    poseImg:          POSE_MAP[luna?.pose]  ?? catSitStill,
    sceneImg:         SCENE_MAP[luna?.scene] ?? afternoonScene,
    streakCelebrate:  luna?.streak_celebrate ?? false,
  }
}
