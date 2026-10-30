from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import current_user, admin_user
from app.models import User, StudentProfile, Skill, CareerRole, RoleSkillRequirement, LearningResource, StudentAssessment, StudentSkillRating, LearningRoadmap, RoadmapItem, LearningProgress
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut, AssessmentIn, RoleIn
from app.security import hash_password, verify_password, create_access_token
from app.services.analysis import analyze_competencies
from app.services.recommender import recommend

router = APIRouter()

@router.post("/auth/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=data.email.lower()).first():
        raise HTTPException(409, "Email already registered")
    user = User(email=data.email.lower(), full_name=data.full_name, hashed_password=hash_password(data.password))
    db.add(user); db.flush(); db.add(StudentProfile(user_id=user.id)); db.commit(); db.refresh(user)
    return user

@router.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    return TokenOut(access_token=create_access_token(str(user.id)))

@router.post("/auth/logout")
def logout(_: User = Depends(current_user)):
    # JWT access tokens are stateless; clients discard the token. Short expiry bounds exposure.
    return {"message": "Logged out. Discard the access token on the client."}

@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)): return user

@router.get("/skills")
def skills(db: Session = Depends(get_db)):
    return [{"id": x.id, "name": x.name, "category": x.category} for x in db.query(Skill).order_by(Skill.name).all()]

@router.get("/career-roles")
def roles(db: Session = Depends(get_db)):
    return [{"id": x.id, "name": x.name, "description": x.description} for x in db.query(CareerRole).order_by(CareerRole.name).all()]

@router.post("/students/assessments", status_code=201)
def assessment(data: AssessmentIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    ids = {x.id for x in db.query(Skill).filter(Skill.id.in_([r.skill_id for r in data.ratings])).all()}
    if any(r.skill_id not in ids for r in data.ratings): raise HTTPException(422, "Assessment contains an unknown skill")
    if len({r.skill_id for r in data.ratings}) != len(data.ratings): raise HTTPException(422, "Each skill may appear once per assessment")
    a = StudentAssessment(user_id=user.id); db.add(a); db.flush()
    db.add_all([StudentSkillRating(assessment_id=a.id, skill_id=r.skill_id, level=r.level) for r in data.ratings]); db.commit()
    return {"id": a.id, "recorded_skills": len(data.ratings), "message": "Assessment saved"}

@router.get("/students/assessment-history")
def assessment_history(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(StudentAssessment).filter_by(user_id=user.id).order_by(StudentAssessment.assessed_at.desc()).all()
    return [{"id": a.id, "assessed_at": a.assessed_at, "ratings": [{"skill_id": r.skill_id, "level": r.level} for r in a.ratings]} for a in rows]

@router.put("/students/profile")
def profile(data: dict, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if "institution" in data: p.institution = str(data["institution"])[:200]
    if "target_role_id" in data:
        if data["target_role_id"] is not None and not db.get(CareerRole, data["target_role_id"]): raise HTTPException(404, "Role not found")
        p.target_role_id = data["target_role_id"]
    db.commit(); return {"institution": p.institution, "target_role_id": p.target_role_id}

@router.post("/competency/analyze")
def analyze(data: RoleIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    try: return analyze_competencies(db, user.id, data.role_id)
    except ValueError as e: raise HTTPException(404, str(e))

@router.post("/recommendations")
def recommendations(data: RoleIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return recommend(db, user.id, data.role_id)

@router.post("/roadmap")
def create_roadmap(data: RoleIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not db.get(CareerRole, data.role_id): raise HTTPException(404, "Role not found")
    analysis = analyze_competencies(db, user.id, data.role_id)
    ranked = [s for s in analysis["skills"] if s["gap"] > 0]
    if not ranked: raise HTTPException(400, "Complete a skill assessment before creating a roadmap")
    recs = recommend(db, user.id, data.role_id, limit=50)
    roadmap = LearningRoadmap(user_id=user.id, role_id=data.role_id); db.add(roadmap); db.flush()
    for seq, gap in enumerate(ranked, 1):
        resource = next((r for r in recs if r["skill"] == gap["skill"]), None)
        if not resource: continue
        db.add(RoadmapItem(roadmap_id=roadmap.id, resource_id=resource["resource_id"], skill_id=gap["skill_id"], sequence=seq,
                           priority=gap["priority"], target_level=gap["required_level"], assignment=f"Complete a practical {gap['skill']} exercise and document the result."))
    db.commit(); return roadmap_view(db, roadmap)

def roadmap_view(db: Session, roadmap: LearningRoadmap):
    items=[]
    for i in roadmap.items:
        r=db.get(LearningResource, i.resource_id); s=db.get(Skill, i.skill_id)
        items.append({"id":i.id,"sequence":i.sequence,"skill":s.name,"priority":i.priority,"target_level":i.target_level,"status":i.status,
                      "assignment":i.assignment,"resource":{"id":r.id,"title":r.title,"url":r.url,"duration_hours":r.duration_hours}})
    return {"id":roadmap.id,"role_id":roadmap.role_id,"items":items,"completion_percent":round(100*sum(i["status"]=="completed" for i in items)/len(items)) if items else 0}

@router.get("/roadmap")
def get_roadmap(db: Session = Depends(get_db), user: User = Depends(current_user)):
    roadmaps=db.query(LearningRoadmap).filter_by(user_id=user.id).order_by(LearningRoadmap.created_at.desc()).all()
    return [roadmap_view(db,r) for r in roadmaps]

@router.patch("/roadmap/items/{item_id}")
def update_item(item_id: int, data: dict, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item=db.get(RoadmapItem,item_id)
    if not item or db.get(LearningRoadmap,item.roadmap_id).user_id != user.id: raise HTTPException(404,"Roadmap item not found")
    status=data.get("status")
    if status not in {"not_started","in_progress","completed"}: raise HTTPException(422,"Invalid status")
    item.status=status; db.add(LearningProgress(user_id=user.id,roadmap_item_id=item.id,progress_percent=100 if status=="completed" else 50 if status=="in_progress" else 0)); db.commit()
    return {"id":item.id,"status":item.status}

@router.get("/analytics")
def analytics(db: Session = Depends(get_db), user: User = Depends(current_user)):
    history=db.query(StudentAssessment).filter_by(user_id=user.id).order_by(StudentAssessment.assessed_at.asc()).all()
    roadmap=db.query(LearningRoadmap).filter_by(user_id=user.id).order_by(LearningRoadmap.created_at.desc()).first()
    levels=[]
    for a in history:
        levels.append({"assessed_at":a.assessed_at,"average_level":round(sum(x.level for x in a.ratings)/len(a.ratings),2) if a.ratings else 0})
    return {"assessment_count":len(history),"skill_history":levels,"roadmap":roadmap_view(db,roadmap) if roadmap else None}

@router.get("/admin/users")
def admin_users(db: Session = Depends(get_db), _: User = Depends(admin_user)):
    return [{"id":u.id,"email":u.email,"full_name":u.full_name,"role":u.role,"is_active":u.is_active} for u in db.query(User).all()]

@router.get("/admin/resources")
def admin_resources(db: Session = Depends(get_db), _: User = Depends(admin_user)):
    return [{"id":r.id,"title":r.title,"type":r.resource_type,"difficulty":r.difficulty} for r in db.query(LearningResource).order_by(LearningResource.title).all()]

@router.post("/admin/roles", status_code=201)
def admin_role(data: dict, db: Session = Depends(get_db), _: User = Depends(admin_user)):
    name = str(data.get("name", "")).strip()
    requirements = data.get("requirements", [])
    if not name or len(name) > 120 or not requirements: raise HTTPException(422,"Role name and at least one skill requirement are required")
    if db.query(CareerRole).filter_by(name=name).first(): raise HTTPException(409,"Role already exists")
    role = CareerRole(name=name, description=str(data.get("description", ""))[:2000]); db.add(role); db.flush()
    for row in requirements:
        skill = db.get(Skill, row.get("skill_id"))
        level, weight = row.get("recommended_level"), row.get("weight", 1.0)
        if not skill or not isinstance(level, int) or not 1 <= level <= 5 or not isinstance(weight, (int,float)) or not 0 < weight <= 10:
            db.rollback(); raise HTTPException(422,"Each requirement needs a valid skill, level 1–5, and weight above 0 through 10")
        db.add(RoleSkillRequirement(role_id=role.id, skill_id=skill.id, recommended_level=level, minimum_level=max(1,level-1), weight=float(weight), industry_relevance=float(row.get("industry_relevance",.7))))
    db.commit(); return {"id":role.id,"name":role.name,"requirements_added":len(requirements)}

@router.get("/admin/analytics")
def admin_analytics(db: Session = Depends(get_db), _: User = Depends(admin_user)):
    return {"users":db.query(User).count(),"roles":db.query(CareerRole).count(),"skills":db.query(Skill).count(),
            "resources":db.query(LearningResource).count(),"assessments":db.query(StudentAssessment).count()}

@router.post("/admin/resources", status_code=201)
def admin_resource(data: dict, db: Session = Depends(get_db), _: User = Depends(admin_user)):
    required={"title","description","skills_text","difficulty","resource_type","duration_hours","url"}
    if not required.issubset(data): raise HTTPException(422,"Missing resource fields")
    r=LearningResource(**{k:data[k] for k in required}); db.add(r); db.commit(); db.refresh(r)
    return {"id":r.id,"title":r.title}
