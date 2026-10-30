# Recommendation methodology

The implementation uses a deterministic hybrid ranking function, not a trained model. It vectorizes each resource's title, description, and skill tags using scikit-learn TF-IDF. A per-gap query is compared to resource vectors with cosine similarity. For a resource/gap pair, the score is:

`0.50 × cosine_similarity + 0.35 × (gap / 5) + 0.10 × level_fit + 0.05 × explicit_skill_tag_match`

`level_fit = 1 - min(abs(resource_difficulty_level - current_student_level), 5) / 5`.

Difficulty maps to 0, 2, or 4 for beginner, intermediate, and advanced. Each recommendation explanation names the skill, current rating, target, priority, and relevance rationale. Duplicate resource IDs are removed from the returned list; the best-ranked resource assignment is retained. The algorithm does not learn preferences or user behavior, and output scores are ranking signals, not probabilities.

Role profiles and learning resources are illustrative synthetic examples. Evaluation needs a held-out dataset of student contexts and expert/user relevance labels. Suitable future offline measures include Precision@K, Recall@K, and NDCG@K with role-wise splits and a popularity baseline; no metric is reported because no such labeled dataset is included.

Weighted alignment is `100 × Σ(weight × min(current, recommended)) / Σ(weight × recommended)`. Missing ratings default to level 0. A zero denominator returns 0. A gap is `max(0, recommended_level - current_level)`. These are competency summaries and must not be interpreted as hiring likelihood.
