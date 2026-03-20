# CareCopilot AI — Frontend Deployment Guide

## Deploy to Vercel (5 minutes)

### 1. Push the frontend folder to GitHub
```bash
cd healthcare-rag-agent/frontend
git init
git add .
git commit -m "feat: CareCopilot AI Next.js frontend v2.0"
git remote add origin https://github.com/YOUR_USER/carecopilot-frontend.git
git push -u origin main
```

### 2. Import to Vercel
- Go to https://vercel.com/new
- Click **Import Git Repository**
- Select your `carecopilot-frontend` repo
- Vercel auto-detects Next.js — click **Deploy**

### 3. Set Environment Variables in Vercel dashboard
| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.onrender.com` |
| `NEXT_PUBLIC_APP_NAME` | `CareCopilot AI` |

---

## Local Development
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL to http://localhost:8000
npm run dev
```

Open http://localhost:3000

---

## Portal URLs (after login, auto-routed by role)

| Role | Path |
|---|---|
| Patient | `/patient/dashboard` |
| Doctor | `/doctor/dashboard` |
| Admin / Superadmin | `/admin/dashboard` |
| Caregiver | `/caregiver/dashboard` |

---

## Pages Built

### Auth
- `/auth/login` — Email + password login with JWT
- `/auth/register` — Role selector (patient / doctor / caregiver) + signup
- `/auth/otp` — 6-digit OTP email verification
- `/auth/forgot-password` — Password reset flow

### Patient Portal
- `/patient/dashboard` — Hero greeting, risk alerts, quick actions, AI insights, activity feed
- `/patient/ai-chat` — Full AI chat interface with suggested prompts
- `/patient/records` — Upload & analyze medical reports (PDF/image)
- `/patient/tracking` — Symptom, vitals, hydration, sleep, meds, activity logger
- `/patient/prescriptions` — Active Rx list, refill requests, order tracking
- `/patient/consultations` — Book & manage video/phone consultations
- `/patient/insurance` — Insurance card, verification status, coverage details
- `/patient/marketplace` — Care products & medications
- `/patient/settings` — Profile, privacy, data export

### Doctor (Clinical) Portal
- `/doctor/dashboard` — Stats, patient queue, upcoming consultations, risk queue
- `/doctor/patients` — Patient list with search, filter, risk indicators
- `/doctor/availability` — Weekly schedule builder with toggle + time pickers

### Admin Portal
- `/admin/dashboard` — KPIs, active alerts (resolve), failed jobs (retry), doctor approvals
- `/admin/users` — Paginated user table with role filter
- `/admin/audit` — System audit log with pagination

### Caregiver Portal
- `/caregiver/dashboard` — Quick actions, patient overview

---

## Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS with CareCopilot AI design tokens (from Stitch designs)
- **Fonts**: Manrope (headlines) + Inter (body) + Material Symbols
- **State**: Zustand (auth + UI) + TanStack Query (server state)
- **Forms**: react-hook-form + zod validation
- **HTTP**: axios with JWT refresh interceptor
- **Icons**: Google Material Symbols Outlined (web font)
