# PRD.md — Luna Tracker Product Requirements Document

## Overview

**Product Name:** Luna Tracker
**Tagline:** 用 Luna 陪你好好生活
**Type:** Progressive Web App (PWA), mobile-first
**Owner:** Personal portfolio project

Luna Tracker is a personal health tracker where a black cat named Luna reflects the
user's daily habits. Luna's mood and activities change based on meals logged and
running sessions synced from Strava. The goal is to make health tracking feel warm,
personal, and fun — not clinical or punishing.

---

## Problem Statement

The user (developer) is training for a half marathon and wants to manage their diet, but
existing health apps feel cold, generic, and guilt-inducing. They want something
deeply personal — built around their real cat Luna, their real habits (bubble tea,
instant noodles, skipping breakfast), and their real Strava running data.

---

## Target User

Single user — the developer themselves. This is a personal tool, not a multi-user
product. All data is scoped to one authenticated user via Strava OAuth.

---

## Core Features

### F1 — Strava OAuth Login
- User authenticates via Strava (OAuth 2.0 Authorization Code Flow)
- No separate username/password — Strava IS the login
- Access token and refresh token stored securely in Supabase
- Token auto-refresh when expired (6-hour expiry)

### F2 — Daily Dashboard (Main Screen)
- Shows today's date and current time period (morning / afternoon / evening)
- Luna is displayed in the correct scene based on time of day
- Luna's pose reflects the meal logged for the current time period
- Running card appears if Strava activity was synced today
- Five habit indicators: Breakfast / Lunch / Dinner / Snack / Run

### F3 — Meal Logging
- Log meals for Breakfast, Lunch, Dinner, and Snack
- Snack has no fixed time — it can be logged at any point during the day
- Each meal entry includes:
  - Description (free text, e.g. "燕麥", "泡麵", "手搖飲")
  - Health Score: 0–10 (user-entered; score ≥ 7 counts as healthy)
  - Special tags: 🧋 Bubble Tea, 🍜 Instant Noodles (triggers shocked pose)
- One entry per meal slot per day
- Can edit/update the same slot before midnight

### F4 — Luna State System

Luna uses a **3-layer priority system**. Higher layers override lower ones.

**Layer 1 — Time Base Poses (always running, lowest priority)**

| Time Period | Hours | Pose File | Vibe |
|---|---|---|---|
| Morning | 05:00–10:59 | `cat_sit_still.png` | Sitting up, waiting for you |
| Afternoon | 11:00–16:59 | `cat_chilling.png` | Lying flat, lazy afternoon |
| Evening | 17:00–19:59 | `cat_stretch.png` | Stretching, hinting at movement |
| Night | 20:00–04:59 | `sleepy_cat.png` | Curled up asleep |

**Layer 2 — Event Poses (triggered by user action, last 2 hours, override Layer 1)**

| Event | Pose File | Duration |
|---|---|---|
| Logged healthy food | `cat_tickling.png` | 2 hours |
| Logged unhealthy food | `unhappy_cat.png` | 2 hours |
| Strava run synced | `playful_cat.png` | 2 hours |

Priority within Layer 2: run > healthy > unhealthy

**Layer 3 — Special Poses (highest priority, override everything)**

| Trigger | Pose File | Duration |
|---|---|---|
| Bubble tea or instant noodles logged | `cat_in_shocked.png` | 1 hour |
| Streak ≥ 3 consecutive healthy days | `cat_one_leg_up.png` | 3-second animation on first open of day |

### F5 — Strava Activity Sync
- On login and on demand, fetch today's activities from Strava API
- Display: distance (km), duration, pace (min/km)
- Triggers Luna cheering pose if any Run activity exists today
- Manual refresh button to pull latest from Strava

### F6 — Streak Tracker
- Count consecutive days where Breakfast, Lunch, and Dinner all scored ≥ 7
- Snack is tracked but does not count toward or against the streak
- Display streak count on dashboard
- Luna wears crown overlay when streak ≥ 3 days
- Streak resets to 0 if a day is missed — no penalty UI, just returns to normal

### F7 — Weekly Summary (Light)
- Simple view of the past 7 days
- Recharts bar/line chart: meal health score per day
- Strava weekly km total
- No detailed analytics — keep it simple

### F8 — PWA Support
- Installable on iPhone via Safari "Add to Home Screen"
- Offline-capable for viewing today's data (cached)
- App icon = Luna avatar
- Splash screen on launch

---

## Out of Scope (v1)

- Push notifications
- Multiple users / sharing
- Calorie counting or macro tracking
- Apple Health / Google Fit integration
- Social features
- Android-specific optimisations (PWA covers both)

---

## User Stories

```
As the user, I want to log my breakfast so Luna reacts and I feel motivated.
As the user, I want to see Luna cheering when I finish a run.
As the user, I want to see my Strava data without switching apps.
As the user, I want to know my healthy eating streak without digging through history.
As the user, I want to install this on my iPhone and use it daily.
As the user, I want to feel warm and not guilty when I eat badly — Luna just waits.
```

---

## Design Principles

1. **Positive only** — no punishment, no red warnings, no shame. Unhealthy = Luna in neutral/waiting pose.
2. **Personal** — Luna is the developer's real cat. The app should feel like it was made for one person.
3. **Warm aesthetic** — handdrawn pastel illustration style, cozy indoor scenes, soft colour palette.
4. **Mobile-first** — designed for 390px width (iPhone), usable on desktop too.
5. **Low friction** — logging a meal should take under 10 seconds.
