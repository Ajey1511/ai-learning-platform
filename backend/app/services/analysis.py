from sqlalchemy.orm import Session
from app.models import CareerRole, RoleSkillRequirement, Skill, StudentAssessment


def analyze_competencies(db: Session, user_id: int, role_id: int) -> dict:
    role = db.get(CareerRole, role_id)
    if not role:
        raise ValueError("Career role not found")
    latest = db.query(StudentAssessment).filter_by(user_id=user_id).order_by(StudentAssessment.assessed_at.desc()).first()
    current = {r.skill_id: r.level for r in latest.ratings} if latest else {}
    reqs = db.query(RoleSkillRequirement).filter_by(role_id=role_id).all()
    rows, numerator, denominator = [], 0.0, 0.0
    for req in reqs:
        skill = db.get(Skill, req.skill_id)
        level = current.get(req.skill_id, 0)
        gap = max(0, req.recommended_level - level)
        numerator += min(level, req.recommended_level) * req.weight
        denominator += req.recommended_level * req.weight
        rows.append({"skill_id": skill.id, "skill": skill.name, "category": skill.category, "current_level": level,
                     "minimum_level": req.minimum_level, "required_level": req.recommended_level, "gap": gap,
                     "weight": req.weight, "priority": "high" if gap >= 3 else "medium" if gap >= 1 else "low"})
    alignment = round(100 * numerator / denominator, 1) if denominator else 0.0
    return {"role": role.name, "role_id": role.id, "alignment_percent": alignment,
            "readiness": "strong" if alignment >= 80 else "developing" if alignment >= 50 else "early",
            "skills": sorted(rows, key=lambda x: (-x["gap"] * x["weight"], x["skill"]))}
