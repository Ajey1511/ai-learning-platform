# Public demo deployment

This setup uses Neon for hosted PostgreSQL, Render for the FastAPI Docker service, and Vercel for the Vite frontend. Free tiers are suitable for an academic demo, with cold starts and quota limits. Render's free web services spin down after 15 minutes idle; its free Postgres databases expire after 30 days, so use an external database for persistent demo data. Neon's current Free plan includes 1 GB per project and 100 compute-hours monthly; it suspends compute at the limit but preserves database storage. Review the linked provider limits before deployment.

## 1. Create the hosted database

1. Create a Neon project and database in the Neon console.
2. Copy the pooled PostgreSQL connection string and keep it private. Its format is typically `postgresql://...`; this backend converts that scheme to the pinned psycopg 3 SQLAlchemy dialect.
3. Do not commit the connection string or put it in the frontend's `VITE_*` variables.

## 2. Deploy the API on Render

1. Sign in to Render and create a Blueprint from the GitHub repository `Ajey1511/name-ai-learning-platform`, or create a Docker Web Service manually.
2. The repository includes `render.yaml`. For manual Docker setup, use Dockerfile path `backend/Dockerfile` and Docker context `backend`.
3. Configure these environment values in Render's service settings:
   - `DATABASE_URL`: the Neon connection string.
   - `SECRET_KEY`: generate a long random value locally (for example with Python `secrets.token_urlsafe(48)`) and paste it directly into Render.
   - `CORS_ORIGINS`: update this after Vercel gives you the frontend URL; enter the exact origin, such as `https://your-site.vercel.app`, without a trailing slash.
4. Wait for the deploy to pass. Check `https://<render-service>.onrender.com/health` and `/docs`. The container applies the Alembic schema migration before starting the API.

## 3. Deploy the frontend on Vercel

1. Import `Ajey1511/name-ai-learning-platform` into Vercel.
2. Set **Root Directory** to `frontend`; framework preset **Vite**; build command `npm run build`; output directory `dist`.
3. Add `VITE_API_URL` with the API base URL, for example `https://<render-service>.onrender.com/api/v1`. Vite embeds this value during the build, so redeploy after changing it.
4. Deploy. The included `frontend/vercel.json` rewrites browser routes to the React entry page.
5. Copy the Vercel production origin and add it to Render's `CORS_ORIGINS`. Save and redeploy the API.

## 4. Verify the public demo

1. Open the Vercel URL and register a test student account.
2. Submit an assessment, run a role analysis, generate recommendations and a roadmap, then update one roadmap item's status.
3. Reload the page and check that data persists through Neon.
4. Keep real personal or student data out of this academic demo. Free service cold starts can delay the first API request after inactivity.

## Environment variables

| Service | Variable | Value |
|---|---|---|
| Render API | `DATABASE_URL` | Private Neon connection string |
| Render API | `SECRET_KEY` | Random secret generated locally |
| Render API | `CORS_ORIGINS` | Exact Vercel frontend origin |
| Vercel frontend | `VITE_API_URL` | Render API URL ending in `/api/v1` |

Do not put secrets in GitHub, Vercel's `VITE_*` variables, screenshots, or chat. `VITE_*` values are included in browser-delivered code and are public.

## Provider notes

- [Render free plan limits](https://render.com/docs/free): free web services spin down after 15 minutes idle. Free Render Postgres expires after 30 days, so this guide uses Neon instead.
- [Neon Free plan limits](https://github.com/neondatabase/website/blob/main/content/faqs/free-plan-limits-and-quotas.md): quota exhaustion suspends compute until reset or upgrade; stored database data is retained.
- [Render Docker deploys](https://render.com/docs/docker) and [Vercel Vite deployments](https://vercel.com/docs/frameworks/frontend/vite).
