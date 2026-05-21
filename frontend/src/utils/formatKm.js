/** Format km for display — 2 decimals (value already synced with Strava app rounding). */
export function formatKm(km) {
  if (km == null || Number.isNaN(Number(km))) return null
  return Number(km).toFixed(2)
}
