from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from app.models import LearningResource, Recommendation
from app.services.analysis import analyze_competencies


def recommend(db: Session, user_id: int, role_id: int, limit: int = 8) -> list[dict]:
    analysis = analyze_competencies(db, user_id, role_id)
    gaps = [s for s in analysis["skills"] if s["gap"] > 0]
    resources = db.query(LearningResource).all()
    if not gaps or not resources:
        return []
    corpus = [" ".join([r.title, r.description, r.skills_text]) for r in resources]
    queries = [f"{g['skill']} {g['category']} competency practice course project" for g in gaps]
    matrix = TfidfVectorizer(stop_words="english").fit_transform(corpus + queries)
    similarities = cosine_similarity(matrix[len(resources):], matrix[:len(resources)])
    result = []
    for ridx, gap in enumerate(gaps):
        for cidx, resource in enumerate(resources):
            text = corpus[cidx].lower()
            lexical = similarities[ridx][cidx]
            explicit_match = gap["skill"].lower() in (resource.skills_text + " " + resource.title).lower()
            difficulty = {"beginner": 0, "intermediate": 2, "advanced": 4}.get(resource.difficulty, 2)
            level_fit = 1 - min(abs(difficulty - gap["current_level"]), 5) / 5
            score = .50 * float(lexical) + .35 * (gap["gap"] / 5) + .10 * level_fit + .05 * explicit_match
            if explicit_match or lexical > .04:
                explanation = (f"{gap['skill']} is recommended because your current proficiency is {gap['current_level']}, "
                               f"while the selected {analysis['role']} role suggests level {gap['required_level']}. "
                               f"This is a {gap['priority']}-priority competency gap. The resource's content is relevant to this skill.")
                result.append({"resource_id": resource.id, "title": resource.title, "type": resource.resource_type,
                               "difficulty": resource.difficulty, "duration_hours": resource.duration_hours,
                               "url": resource.url, "skill": gap["skill"], "score": round(score, 4), "explanation": explanation})
    result.sort(key=lambda x: (-x["score"], x["title"]))
    # Persist ranked recommendations, while returning each resource only once.
    unique, seen = [], set()
    for item in result:
        if item["resource_id"] in seen:
            continue
        seen.add(item["resource_id"])
        unique.append(item)
        db.add(Recommendation(user_id=user_id, role_id=role_id, resource_id=item["resource_id"], score=item["score"], explanation=item["explanation"]))
        if len(unique) >= limit:
            break
    db.commit()
    return unique
