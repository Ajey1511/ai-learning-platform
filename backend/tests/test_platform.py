import os
os.environ["DATABASE_URL"] = "sqlite:///./test_learning.db"
os.environ["SECRET_KEY"] = "test-secret"
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine
from app.seed import seed

Base.metadata.drop_all(engine); Base.metadata.create_all(engine); seed()
client = TestClient(app)

def register():
    return client.post("/api/v1/auth/register", json={"email":"student@example.org","password":"secure-pass-123","full_name":"Test Student"})

def test_registration_login_and_protected_route():
    assert register().status_code == 201
    token=client.post("/api/v1/auth/login",json={"email":"student@example.org","password":"secure-pass-123"}).json()["access_token"]
    assert client.get("/api/v1/auth/me",headers={"Authorization":f"Bearer {token}"}).status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401

def test_assessment_analysis_recommendations_and_roadmap():
    token=client.post("/api/v1/auth/login",json={"email":"student@example.org","password":"secure-pass-123"}).json()["access_token"]
    h={"Authorization":f"Bearer {token}"}
    skills=client.get("/api/v1/skills").json(); role=next(r for r in client.get("/api/v1/career-roles").json() if r["name"]=="Data Analyst")
    ids={s["name"]:s["id"] for s in skills}
    assert client.post("/api/v1/students/assessments",headers=h,json={"ratings":[{"skill_id":ids["SQL"],"level":1},{"skill_id":ids["Statistics"],"level":2}]}).status_code==201
    result=client.post("/api/v1/competency/analyze",headers=h,json={"role_id":role["id"]}).json()
    assert result["alignment_percent"] < 100 and any(s["gap"]>0 for s in result["skills"])
    recs=client.post("/api/v1/recommendations",headers=h,json={"role_id":role["id"]}).json()
    assert recs and all(x["explanation"] and 0<=x["score"]<=1.5 for x in recs)
    roadmap=client.post("/api/v1/roadmap",headers=h,json={"role_id":role["id"]}).json()
    assert roadmap["items"]
    item=roadmap["items"][0]
    assert client.patch(f"/api/v1/roadmap/items/{item['id']}",headers=h,json={"status":"completed"}).status_code==200

def test_role_based_access_and_validation():
    assert client.post("/api/v1/auth/register",json={"email":"x@x.com","password":"short","full_name":"X"}).status_code==422
