# Viva questions and answers

1. **What problem does the platform address?** It makes a student's self-assessed technical competencies comparable with an illustrative target-role profile and turns the gaps into learning suggestions.
2. **Why a modular monolith?** The modules have clear boundaries, but a single deployable keeps a final-year project easier to run and reason about than distributed services.
3. **How are passwords protected?** Passlib bcrypt hashes passwords; plaintext values are never stored.
4. **What does the access token contain?** A signed JWT with a user identifier subject and expiry. It is bearer authentication, so transport must use HTTPS in deployment.
5. **How is an assessment stored?** Each submission creates a timestamped assessment snapshot with one rating per skill, preserving retake history.
6. **How is a skill gap calculated?** The nonnegative difference between suggested role level and current rating.
7. **How is overall alignment computed?** A weighted sum of capped current levels divided by the weighted suggested levels, multiplied by 100. A zero denominator yields zero.
8. **What does the alignment percentage mean?** A weighted competency comparison only; it does not estimate employability or hiring probability.
9. **Is the recommendation model trained?** No. It is a deterministic hybrid content ranker that uses TF-IDF, cosine similarity, gap priority, difficulty fit, and explicit tags.
10. **Why use TF-IDF?** It provides a reproducible way to represent resource text and skill queries while reducing the weight of common words.
11. **What is cosine similarity doing?** It measures directional similarity between TF-IDF vectors for a gap query and a resource document.
12. **How are recommendations explained?** Each explanation reports the student's current and target levels, gap priority, and content relevance.
13. **How could the recommender be evaluated?** Collect relevance labels for student-role-resource contexts, separate data into evaluation splits, compare to simple baselines, and report ranking metrics such as NDCG@K and Recall@K.
14. **How does the roadmap use the analysis?** It orders positive gaps by weighted gap importance and assigns the top matching resource to each skill when available.
15. **How is progress persisted?** Roadmap status updates modify the item and create a progress record for the authenticated owner.
16. **Why use Alembic?** It provides versioned, repeatable schema changes rather than requiring users to manually create database tables.
17. **How is unauthorized access restricted?** JWT authentication resolves a current user; owner checks scope roadmap changes; admin endpoints require the admin role.
18. **What are the main limitations?** Self-assessment bias, illustrative role requirements, small sample resource catalog, and no real interaction data or evaluated trained model.
19. **How would you add a new career role?** Add a `career_roles` row and associated weighted `role_skill_requirements` rows using existing skill IDs.
20. **What is a responsible next step?** Validate role profiles with domain experts and students, improve objective assessment evidence, and evaluate ranking quality on consented real relevance data.
