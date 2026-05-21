/** User-facing meal names (API still uses breakfast | lunch | dinner | snack). */
export const MEAL_LABELS = {
  breakfast: 'Brekkie',
  lunch: 'Lunch',
  dinner: 'Dinner',
  snack: 'Snack',
}

/** Plural for insight copy, e.g. "Your brekkies average …" */
export function mealLabelPlural(mealType) {
  if (mealType === 'breakfast') return 'brekkies'
  return `${MEAL_LABELS[mealType].toLowerCase()}s`
}
