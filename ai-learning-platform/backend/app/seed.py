from app.db import Base, engine, SessionLocal
from app.models import Skill, CareerRole, RoleSkillRequirement, LearningResource, ModelMetadata, Project

SKILLS = [
 ("Python","Programming"),("Java","Programming"),("SQL","Data"),("Database Management","Data"),("Data Structures and Algorithms","Computer Science"),("Statistics","Data"),("Machine Learning","AI"),("Deep Learning","AI"),("Data Visualization","Data"),("HTML and CSS","Web"),("JavaScript","Web"),("React","Web"),("Git and GitHub","Tools"),("Cloud Computing","Cloud"),("Problem Solving","Core")]
ROLE_SKILLS = {
 "Data Analyst":{"SQL":4,"Statistics":4,"Data Visualization":4,"Python":3,"Database Management":3,"Problem Solving":3},
 "Data Scientist":{"Python":4,"Statistics":4,"Machine Learning":4,"SQL":3,"Data Visualization":3,"Deep Learning":2},
 "Machine Learning Engineer":{"Python":5,"Machine Learning":4,"Deep Learning":4,"Cloud Computing":3,"Data Structures and Algorithms":4,"Git and GitHub":3},
 "Python Developer":{"Python":5,"Data Structures and Algorithms":4,"SQL":3,"Git and GitHub":3,"Problem Solving":4},
 "Full-Stack Developer":{"HTML and CSS":4,"JavaScript":4,"React":4,"Python":3,"SQL":3,"Git and GitHub":3},
 "Backend Developer":{"Python":4,"Java":3,"SQL":4,"Database Management":4,"Cloud Computing":3,"Git and GitHub":3},
 "Cloud Engineer":{"Cloud Computing":5,"Python":3,"Linux":3,"Git and GitHub":3,"Database Management":2},
 "AI Engineer":{"Python":5,"Machine Learning":4,"Deep Learning":4,"Statistics":3,"Cloud Computing":3,"Data Structures and Algorithms":3}}
RESOURCES = [
 ("Python Foundations","Variables, functions, data structures and practical scripting.","Python programming fundamentals", "beginner","course",8,"https://docs.python.org/3/tutorial/"),
 ("SQL for Analysis","Query relational data with joins, aggregation and window functions.","SQL database analytics", "beginner","course",6,"https://sqlbolt.com/"),
 ("Statistics Practice Lab","Descriptive statistics, probability and inference with exercises.","Statistics data probability", "intermediate","course",7,"https://www.openintro.org/book/os/"),
 ("Machine Learning Study Path","Supervised learning, model selection and evaluation exercises.","Python Machine Learning model evaluation", "intermediate","course",12,"https://scikit-learn.org/stable/user_guide.html"),
 ("Build a Data Dashboard","Create a small dashboard and explain the choices behind its charts.","Data Visualization project dashboard", "intermediate","project",5,"https://public.tableau.com/app/learn/sample-data"),
 ("Neural Network Fundamentals","Explore neural network training concepts and implementation.","Deep Learning neural networks", "advanced","course",10,"https://pytorch.org/tutorials/"),
 ("Web Portfolio Project","Build and publish an accessible responsive portfolio.","HTML CSS JavaScript React web", "intermediate","project",8,"https://react.dev/learn"),
 ("Git Collaboration Exercise","Practice branches, pull requests and conflict resolution.","Git and GitHub version control", "beginner","project",3,"https://docs.github.com/en/get-started/quickstart"),
 ("Cloud Deployment Lab","Package a service and deploy it with a managed cloud workflow.","Cloud Computing deployment", "intermediate","project",6,"https://12factor.net/"),
 ("Algorithms Practice Set","Solve and discuss common algorithm and data structure problems.","Data Structures and Algorithms Problem Solving", "intermediate","project",8,"https://visualgo.net/en")]


def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Skill).count(): return
        skills={}
        for name,category in SKILLS:
            obj=Skill(name=name,category=category,description=f"Synthetic catalog entry for {name}."); db.add(obj); db.flush(); skills[name]=obj
        if "Linux" not in skills:
            obj=Skill(name="Linux",category="Tools",description="Synthetic catalog entry for Linux.");db.add(obj);db.flush();skills["Linux"]=obj
        for name, reqs in ROLE_SKILLS.items():
            role=CareerRole(name=name,description="Sample role profile; requirements are illustrative and are not verified employer specifications.");db.add(role);db.flush()
            for sk, level in reqs.items(): db.add(RoleSkillRequirement(role_id=role.id,skill_id=skills[sk].id,weight=1.0 if level>=4 else .8,minimum_level=max(1,level-1),recommended_level=level,industry_relevance=.9 if level>=4 else .75))
        for title,description,tags,difficulty,kind,hours,url in RESOURCES: db.add(LearningResource(title=title,description=description,skills_text=tags,difficulty=difficulty,resource_type=kind,duration_hours=hours,url=url))
        for title, skill, description, hours, difficulty in [
            ("Data dashboard", "Data Visualization", "Build a dashboard from a public sample dataset and explain chart choices.", 5, "intermediate"),
            ("Algorithms practice set", "Data Structures and Algorithms", "Solve and explain a focused set of data structure exercises.", 8, "intermediate"),
            ("Web portfolio", "React", "Build an accessible responsive portfolio site.", 8, "intermediate"),
            ("Cloud deployment lab", "Cloud Computing", "Containerize a small API and document deployment steps.", 6, "intermediate"),
        ]: db.add(Project(title=title, skill_id=skills[skill].id, description=description, estimated_hours=hours, difficulty=difficulty))
        db.add(ModelMetadata(name="Hybrid content and gap ranker",version="1.0",approach="TF-IDF/cosine relevance blended with skill gap, level fit and explicit tag match. No supervised model training.",trained=False))
        db.commit()

if __name__ == "__main__": seed()
