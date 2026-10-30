# API contracts

All routes use `/api/v1`. OpenAPI UI is at `/docs` and the schema at `/openapi.json`.

| Method | Route | Access | Purpose |
|---|---|---|---|
| POST | `/auth/register` | Public | Create student account |
| POST | `/auth/login` | Public | Return bearer JWT |
| POST | `/auth/logout` | Authenticated | Acknowledge client-side token discard |
| GET | `/auth/me` | Authenticated | Current user |
| GET | `/skills`, `/career-roles` | Public | Catalogs |
| POST | `/students/assessments` | Student | Save a 0–5 assessment snapshot |
| GET | `/students/assessment-history` | Student | Read own assessment history |
| PUT | `/students/profile` | Student | Update own profile preferences |
| POST | `/competency/analyze` | Student | Analyze role alignment |
| POST | `/recommendations` | Student | Rank and persist resources |
| GET/POST | `/roadmap` | Student | Read or generate own roadmap |
| PATCH | `/roadmap/items/{id}` | Owner | Update item status |
| GET | `/analytics` | Student | Read persisted assessment and roadmap summaries |
| GET | `/admin/users` | Admin | List accounts |
| GET | `/admin/resources`, `/admin/analytics` | Admin | List catalog and platform counts |
| POST | `/admin/resources`, `/admin/roles` | Admin | Add a resource or role with skill requirements |

Authenticated requests use `Authorization: Bearer <access_token>`. Validation errors return FastAPI's 422 response; missing authentication is 401; admin-only access is 403; duplicate email is 409. A missing role/resource is 404. Admin account bootstrapping and JWT revocation are not yet exposed as operational features; create admin users through a controlled database bootstrap before enabling the admin API.
