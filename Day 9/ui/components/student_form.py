import streamlit as st
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

def create_student_form(existing_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Create a student profile form"""
    
    st.subheader("Student Profile Information")
    
    # Pre-fill with existing data if provided
    defaults = existing_data or {}
    
    with st.form("student_profile_form"):
        # Basic Information
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name *",
                value=defaults.get("name", ""),
                placeholder="Enter your full name"
            )
            
            email = st.text_input(
                "Email Address *",
                value=defaults.get("email", ""),
                placeholder="your.email@university.edu"
            )
            
            graduation_year = st.selectbox(
                "Expected Graduation Year *",
                options=list(range(2024, 2030)),
                index=list(range(2024, 2030)).index(defaults.get("graduation_year", 2025)) 
                      if defaults.get("graduation_year") in range(2024, 2030) else 1
            )
        
        with col2:
            degree = st.selectbox(
                "Degree Program *",
                options=["Bachelor of Science", "Bachelor of Arts", "Bachelor of Engineering", 
                        "Master of Science", "Master of Arts", "Master of Engineering", "MBA", "PhD"],
                index=0 if not defaults.get("degree") else 
                      ["Bachelor of Science", "Bachelor of Arts", "Bachelor of Engineering", 
                       "Master of Science", "Master of Arts", "Master of Engineering", "MBA", "PhD"].index(defaults.get("degree"))
                      if defaults.get("degree") in ["Bachelor of Science", "Bachelor of Arts", "Bachelor of Engineering", 
                                                   "Master of Science", "Master of Arts", "Master of Engineering", "MBA", "PhD"] else 0
            )
            
            major = st.selectbox(
                "Major/Field of Study *",
                options=["Computer Science", "Software Engineering", "Data Science", "Information Technology",
                        "Electrical Engineering", "Mechanical Engineering", "Business Administration",
                        "Marketing", "Finance", "Economics", "Psychology", "Other"],
                index=0 if not defaults.get("major") else
                      ["Computer Science", "Software Engineering", "Data Science", "Information Technology",
                       "Electrical Engineering", "Mechanical Engineering", "Business Administration",
                       "Marketing", "Finance", "Economics", "Psychology", "Other"].index(defaults.get("major"))
                      if defaults.get("major") in ["Computer Science", "Software Engineering", "Data Science", "Information Technology",
                                                  "Electrical Engineering", "Mechanical Engineering", "Business Administration",
                                                  "Marketing", "Finance", "Economics", "Psychology", "Other"] else 0
            )
            
            gpa = st.number_input(
                "GPA (Optional)",
                min_value=0.0,
                max_value=4.0,
                value=defaults.get("gpa", 0.0) if defaults.get("gpa") else 0.0,
                step=0.1,
                format="%.2f"
            )
        
        # Skills Section
        st.subheader("Technical Skills")
        
        # Predefined skill categories
        skill_categories = {
            "Programming Languages": ["Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "Swift", "Kotlin"],
            "Web Technologies": ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Express.js", "Spring Boot"],
            "Data & Analytics": ["SQL", "MongoDB", "PostgreSQL", "Pandas", "NumPy", "Tableau", "Power BI", "Excel"],
            "Cloud & DevOps": ["AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Git", "Linux"],
            "AI & ML": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision"],
            "Other Technologies": ["REST APIs", "GraphQL", "Microservices", "Blockchain", "IoT", "Mobile Development"]
        }
        
        selected_skills = []
        existing_skills = defaults.get("skills", [])
        
        # Create skill selection interface
        for category, skills in skill_categories.items():
            with st.expander(f"{category} Skills"):
                cols = st.columns(3)
                for i, skill in enumerate(skills):
                    with cols[i % 3]:
                        if st.checkbox(skill, value=skill in existing_skills, key=f"skill_{skill}"):
                            selected_skills.append(skill)
        
        # Custom skills input
        custom_skills = st.text_input(
            "Additional Skills (comma-separated)",
            value=", ".join([s for s in existing_skills if s not in [skill for skills in skill_categories.values() for skill in skills]]),
            placeholder="e.g., Figma, Photoshop, Project Management"
        )
        
        if custom_skills:
            selected_skills.extend([skill.strip() for skill in custom_skills.split(",") if skill.strip()])
        
        # Career Interests
        st.subheader("Career Interests & Goals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            interests = st.multiselect(
                "Career Interests",
                options=["Software Development", "Data Science", "Machine Learning", "Web Development",
                        "Mobile Development", "DevOps", "Cloud Computing", "Cybersecurity", "Product Management",
                        "UI/UX Design", "Business Analysis", "Project Management", "Research", "Consulting"],
                default=defaults.get("interests", [])
            )
            
            target_roles = st.multiselect(
                "Target Job Roles",
                options=["Software Engineer", "Data Scientist", "Full Stack Developer", "Frontend Developer",
                        "Backend Developer", "Mobile Developer", "DevOps Engineer", "ML Engineer", 
                        "Product Manager", "Business Analyst", "QA Engineer", "Technical Writer"],
                default=defaults.get("target_roles", [])
            )
        
        with col2:
            target_companies = st.multiselect(
                "Target Companies",
                options=["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla", "Uber",
                        "Airbnb", "Spotify", "Adobe", "Salesforce", "Oracle", "IBM", "Intel", "NVIDIA",
                        "Startup", "Government", "Non-profit", "Other"],
                default=defaults.get("target_companies", [])
            )
            
            preferred_locations = st.multiselect(
                "Preferred Work Locations",
                options=["San Francisco, CA", "Seattle, WA", "New York, NY", "Austin, TX", "Boston, MA",
                        "Chicago, IL", "Los Angeles, CA", "Denver, CO", "Atlanta, GA", "Remote", "Flexible"],
                default=defaults.get("preferred_locations", [])
            )
        
        # Projects & Experience
        st.subheader("Projects & Experience")
        
        # Projects
        projects_text = st.text_area(
            "Key Projects (one per line)",
            value="\n".join([f"{p.get('name', '')}: {p.get('description', '')}" for p in defaults.get("projects", [])]),
            placeholder="Project Name: Brief description of the project and technologies used",
            height=100
        )
        
        # Parse projects
        projects = []
        if projects_text:
            for line in projects_text.split('\n'):
                if ':' in line and line.strip():
                    name, description = line.split(':', 1)
                    projects.append({
                        "name": name.strip(),
                        "description": description.strip(),
                        "technologies": []  # Could be enhanced to extract technologies
                    })
        
        # Experience
        col1, col2 = st.columns(2)
        
        with col1:
            internships = st.text_area(
                "Internship Experience",
                value=defaults.get("internship_experience", ""),
                placeholder="Company, Role, Duration, Key responsibilities",
                height=80
            )
        
        with col2:
            work_experience = st.text_area(
                "Work Experience",
                value=defaults.get("work_experience", ""),
                placeholder="Company, Role, Duration, Key responsibilities", 
                height=80
            )
        
        # Additional Information
        st.subheader("Additional Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            linkedin_url = st.text_input(
                "LinkedIn Profile URL",
                value=defaults.get("linkedin_url", ""),
                placeholder="https://linkedin.com/in/yourprofile"
            )
            
            github_url = st.text_input(
                "GitHub Profile URL",
                value=defaults.get("github_url", ""),
                placeholder="https://github.com/yourusername"
            )
        
        with col2:
            portfolio_url = st.text_input(
                "Portfolio/Website URL",
                value=defaults.get("portfolio_url", ""),
                placeholder="https://yourportfolio.com"
            )
            
            resume_url = st.text_input(
                "Resume URL",
                value=defaults.get("resume_url", ""),
                placeholder="https://drive.google.com/your-resume"
            )
        
        # Preferences
        st.subheader("Referral Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            referral_urgency = st.selectbox(
                "Referral Urgency",
                options=["Low - Exploring opportunities", "Medium - Actively looking", "High - Need referrals ASAP"],
                index=["Low - Exploring opportunities", "Medium - Actively looking", "High - Need referrals ASAP"].index(defaults.get("referral_urgency", "Medium - Actively looking"))
                      if defaults.get("referral_urgency") in ["Low - Exploring opportunities", "Medium - Actively looking", "High - Need referrals ASAP"] else 1
            )
            
            communication_preference = st.selectbox(
                "Preferred Communication",
                options=["Email", "LinkedIn Message", "Phone Call", "Video Call", "Any"],
                index=["Email", "LinkedIn Message", "Phone Call", "Video Call", "Any"].index(defaults.get("communication_preference", "Email"))
                      if defaults.get("communication_preference") in ["Email", "LinkedIn Message", "Phone Call", "Video Call", "Any"] else 0
            )
        
        with col2:
            availability = st.text_input(
                "Availability for Calls/Meetings",
                value=defaults.get("availability", ""),
                placeholder="e.g., Weekdays 6-8 PM EST, Weekends flexible"
            )
            
            max_referrals = st.number_input(
                "Maximum Referrals Needed",
                min_value=1,
                max_value=20,
                value=defaults.get("max_referrals", 5),
                step=1
            )
        
        # Additional notes
        additional_notes = st.text_area(
            "Additional Notes",
            value=defaults.get("additional_notes", ""),
            placeholder="Any additional information you'd like to share with potential referrers",
            height=60
        )
        
        # Form submission
        submitted = st.form_submit_button("Save Profile", type="primary")
        
        if submitted:
            # Validation
            if not all([name, email, graduation_year, degree, major]):
                st.error("Please fill in all required fields marked with *")
                return None
            
            # Email validation
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address")
                return None
            
            # Create student profile
            student_profile = {
                "student_id": defaults.get("student_id", f"student_{str(uuid.uuid4())[:8]}"),
                "name": name,
                "email": email,
                "graduation_year": graduation_year,
                "degree": degree,
                "major": major,
                "gpa": gpa if gpa > 0 else None,
                "skills": list(set(selected_skills)),  # Remove duplicates
                "interests": interests,
                "target_roles": target_roles,
                "target_companies": target_companies,
                "preferred_locations": preferred_locations,
                "projects": projects,
                "internship_experience": internships,
                "work_experience": work_experience,
                "linkedin_url": linkedin_url,
                "github_url": github_url,
                "portfolio_url": portfolio_url,
                "resume_url": resume_url,
                "referral_urgency": referral_urgency,
                "communication_preference": communication_preference,
                "availability": availability,
                "max_referrals": max_referrals,
                "additional_notes": additional_notes,
                "created_at": defaults.get("created_at", datetime.utcnow()),
                "updated_at": datetime.utcnow()
            }
            
            return student_profile
    
    return None

def display_student_profile(profile: Dict[str, Any]):
    """Display a student profile in a formatted way"""
    
    st.subheader(f"👨‍🎓 {profile.get('name', 'Unknown Student')}")
    
    # Basic info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Email:** {profile.get('email', 'N/A')}")
        st.write(f"**Graduation Year:** {profile.get('graduation_year', 'N/A')}")
        st.write(f"**Degree:** {profile.get('degree', 'N/A')}")
    
    with col2:
        st.write(f"**Major:** {profile.get('major', 'N/A')}")
        if profile.get('gpa'):
            st.write(f"**GPA:** {profile.get('gpa', 'N/A'):.2f}")
        st.write(f"**Urgency:** {profile.get('referral_urgency', 'N/A')}")
    
    with col3:
        st.write(f"**Max Referrals:** {profile.get('max_referrals', 'N/A')}")
        st.write(f"**Communication:** {profile.get('communication_preference', 'N/A')}")
        if profile.get('availability'):
            st.write(f"**Availability:** {profile.get('availability', 'N/A')}")
    
    # Skills
    if profile.get('skills'):
        st.write("**Skills:**")
        skills_text = ", ".join(profile['skills'])
        st.write(skills_text)
    
    # Interests and targets
    col1, col2 = st.columns(2)
    
    with col1:
        if profile.get('interests'):
            st.write("**Career Interests:**")
            for interest in profile['interests']:
                st.write(f"• {interest}")
        
        if profile.get('target_roles'):
            st.write("**Target Roles:**")
            for role in profile['target_roles']:
                st.write(f"• {role}")
    
    with col2:
        if profile.get('target_companies'):
            st.write("**Target Companies:**")
            for company in profile['target_companies']:
                st.write(f"• {company}")
        
        if profile.get('preferred_locations'):
            st.write("**Preferred Locations:**")
            for location in profile['preferred_locations']:
                st.write(f"• {location}")
    
    # Projects
    if profile.get('projects'):
        st.write("**Key Projects:**")
        for project in profile['projects']:
            st.write(f"• **{project.get('name', 'Unnamed Project')}:** {project.get('description', 'No description')}")
    
    # Experience
    if profile.get('internship_experience') or profile.get('work_experience'):
        st.write("**Experience:**")
        if profile.get('internship_experience'):
            st.write(f"**Internships:** {profile['internship_experience']}")
        if profile.get('work_experience'):
            st.write(f"**Work Experience:** {profile['work_experience']}")
    
    # Links
    links = []
    if profile.get('linkedin_url'):
        links.append(f"[LinkedIn]({profile['linkedin_url']})")
    if profile.get('github_url'):
        links.append(f"[GitHub]({profile['github_url']})")
    if profile.get('portfolio_url'):
        links.append(f"[Portfolio]({profile['portfolio_url']})")
    if profile.get('resume_url'):
        links.append(f"[Resume]({profile['resume_url']})")
    
    if links:
        st.write("**Links:** " + " | ".join(links))
    
    # Additional notes
    if profile.get('additional_notes'):
        st.write(f"**Additional Notes:** {profile['additional_notes']}")

def create_quick_student_form() -> Optional[Dict[str, Any]]:
    """Create a simplified student form for quick profile creation"""
    
    st.subheader("Quick Student Profile")
    
    with st.form("quick_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", placeholder="Your full name")
            email = st.text_input("Email *", placeholder="your.email@university.edu")
            major = st.selectbox("Major *", ["Computer Science", "Software Engineering", "Data Science", "Other"])
        
        with col2:
            graduation_year = st.selectbox("Graduation Year *", list(range(2024, 2030)))
            target_company = st.selectbox("Primary Target Company", 
                                        ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Other"])
            target_role = st.selectbox("Primary Target Role",
                                     ["Software Engineer", "Data Scientist", "Product Manager", "Other"])
        
        skills = st.multiselect("Top 5 Skills", 
                               ["Python", "Java", "JavaScript", "React", "AWS", "Machine Learning", "SQL"])
        
        submitted = st.form_submit_button("Create Quick Profile", type="primary")
        
        if submitted:
            if not all([name, email, major, graduation_year]):
                st.error("Please fill in all required fields")
                return None
            
            quick_profile = {
                "student_id": f"student_{str(uuid.uuid4())[:8]}",
                "name": name,
                "email": email,
                "graduation_year": graduation_year,
                "degree": "Bachelor of Science",  # Default
                "major": major,
                "skills": skills,
                "interests": [target_role.replace(" Engineer", "").replace(" Scientist", " Science")],
                "target_companies": [target_company] if target_company != "Other" else [],
                "target_roles": [target_role] if target_role != "Other" else [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            return quick_profile
    
    return None