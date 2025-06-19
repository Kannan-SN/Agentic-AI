import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure Streamlit
st.set_page_config(
    page_title="Alumni Referrer Network Builder",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🎓 Alumni Referrer Network Builder")
    st.markdown("**AI-Powered Student-Alumni Referral Matching System**")
    
    # Check if we can import basic modules
    try:
        from config.settings import load_config
        from database.mongodb_client import MongoDBClient
        config = load_config()
        
        # Test database connection
        try:
            db_client = MongoDBClient()
            db_status = db_client.connect()
            if db_status:
                st.success("✅ Database connected successfully!")
            else:
                st.warning("⚠️ Database connection failed, but app will work with limited functionality")
        except Exception as e:
            st.warning(f"⚠️ Database error: {e}")
            db_client = None
        
    except Exception as e:
        st.error(f"❌ Configuration error: {e}")
        st.info("Please check your .env file and ensure all required packages are installed")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Student Profile", "Alumni Demo", "Quick Demo"]
        )
        
        # System Status
        st.header("System Status")
        
        # Check agent availability
        agents_status = {}
        
        try:
            from agents.crew_agent import CrewAlumniAgent
            agents_status['CrewAI'] = "✅"
        except:
            agents_status['CrewAI'] = "❌"
        
        try:
            from agents.langchain_agent import LangChainDomainAgent
            agents_status['LangChain'] = "✅"
        except:
            agents_status['LangChain'] = "❌"
        
        try:
            from agents.langgraph_agent import LangGraphReferralAgent
            agents_status['LangGraph'] = "✅"
        except:
            agents_status['LangGraph'] = "❌"
        
        try:
            from agents.autogen_agent import AutoGenOutreachAgent
            agents_status['AutoGen'] = "✅"
        except:
            agents_status['AutoGen'] = "❌"
        
        st.write("**AI Agents Status:**")
        for agent, status in agents_status.items():
            st.write(f"{status} {agent}")
        
        # RAG Status
        try:
            from rag.rag_pipeline import RAGPipeline
            st.write("✅ RAG Pipeline")
        except:
            st.write("❌ RAG Pipeline")
    
    # Main content based on page selection
    if page == "Dashboard":
        show_dashboard(db_client)
    elif page == "Student Profile":
        show_student_profile(db_client)
    elif page == "Alumni Demo":
        show_alumni_demo(db_client)
    elif page == "Quick Demo":
        show_quick_demo()

def show_dashboard(db_client):
    """Show dashboard"""
    st.header("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if db_client:
        try:
            # Get actual stats from database
            students_count = len(db_client.find_documents("students"))
            alumni_count = len(db_client.find_documents("alumni"))
            referrals_count = len(db_client.find_documents("referrals"))
            
            with col1:
                st.metric("Students", students_count)
            with col2:
                st.metric("Alumni", alumni_count)
            with col3:
                st.metric("Referrals", referrals_count)
            with col4:
                st.metric("Success Rate", "75%")
                
        except Exception as e:
            st.error(f"Error loading stats: {e}")
            show_demo_stats(col1, col2, col3, col4)
    else:
        show_demo_stats(col1, col2, col3, col4)
    
    # Demo charts
    st.subheader("📈 Analytics")
    
    # Sample data for demo
    demo_data = {
        "Company": ["Google", "Microsoft", "Amazon", "Apple", "Meta"],
        "Alumni Count": [45, 38, 42, 35, 28],
        "Referral Success": [85, 78, 82, 75, 88]
    }
    
    df = pd.DataFrame(demo_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(df.set_index("Company")["Alumni Count"])
        st.caption("Alumni Distribution by Company")
    
    with col2:
        st.line_chart(df.set_index("Company")["Referral Success"])
        st.caption("Referral Success Rate by Company")

def show_demo_stats(col1, col2, col3, col4):
    """Show demo statistics"""
    with col1:
        st.metric("Students", 156, "+12")
    with col2:
        st.metric("Alumni", 342, "+25")
    with col3:
        st.metric("Referrals", 89, "+8")
    with col4:
        st.metric("Success Rate", "75%", "↗️")

def show_student_profile(db_client):
    """Show student profile form"""
    st.header("👨‍🎓 Student Profile")
    
    with st.form("student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email *", placeholder="john.doe@university.edu")
            graduation_year = st.selectbox("Graduation Year *", [2024, 2025, 2026, 2027])
            major = st.selectbox("Major *", ["Computer Science", "Software Engineering", "Data Science", "Other"])
        
        with col2:
            target_company = st.selectbox("Target Company", ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Other"])
            target_role = st.selectbox("Target Role", ["Software Engineer", "Data Scientist", "Product Manager", "Other"])
            skills = st.multiselect("Skills", ["Python", "Java", "React", "AWS", "Machine Learning", "SQL"])
            gpa = st.number_input("GPA (Optional)", 0.0, 4.0, 0.0, 0.1)
        
        submitted = st.form_submit_button("Save Profile", type="primary")
        
        if submitted:
            if name and email and graduation_year and major:
                profile_data = {
                    "student_id": f"student_{len(name)}_{graduation_year}",
                    "name": name,
                    "email": email,
                    "graduation_year": graduation_year,
                    "major": major,
                    "target_companies": [target_company] if target_company != "Other" else [],
                    "target_roles": [target_role] if target_role != "Other" else [],
                    "skills": skills,
                    "gpa": gpa if gpa > 0 else None,
                    "created_at": datetime.now().isoformat()
                }
                
                if db_client:
                    try:
                        student_id = db_client.insert_document("students", profile_data)
                        st.success(f"✅ Profile saved successfully! ID: {student_id}")
                    except Exception as e:
                        st.error(f"Error saving profile: {e}")
                else:
                    st.success("✅ Profile created (demo mode - not saved to database)")
                
                # Display created profile
                st.subheader("Created Profile")
                st.json(profile_data)
            else:
                st.error("Please fill in all required fields marked with *")

def show_alumni_demo(db_client):
    """Show alumni demo data"""
    st.header("🎯 Alumni Network Demo")
    
    # Sample alumni data
    alumni_data = [
        {
            "name": "Sarah Chen",
            "company": "Google",
            "role": "Senior Software Engineer",
            "graduation_year": 2019,
            "skills": ["Python", "Go", "Kubernetes", "Machine Learning"],
            "willing_to_refer": True,
            "location": "Mountain View, CA"
        },
        {
            "name": "Michael Rodriguez",
            "company": "Microsoft",
            "role": "Principal Engineer",
            "graduation_year": 2017,
            "skills": ["C#", "Azure", "React", "TypeScript"],
            "willing_to_refer": True,
            "location": "Redmond, WA"
        },
        {
            "name": "Emily Johnson",
            "company": "Amazon",
            "role": "Software Development Manager",
            "graduation_year": 2016,
            "skills": ["Java", "AWS", "Leadership", "System Design"],
            "willing_to_refer": True,
            "location": "Seattle, WA"
        }
    ]
    
    st.subheader("Alumni Profiles")
    
    for i, alumni in enumerate(alumni_data):
        with st.expander(f"{alumni['name']} - {alumni['company']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Company:** {alumni['company']}")
                st.write(f"**Role:** {alumni['role']}")
                st.write(f"**Graduation:** {alumni['graduation_year']}")
            
            with col2:
                st.write(f"**Location:** {alumni['location']}")
                st.write(f"**Willing to Refer:** {'Yes' if alumni['willing_to_refer'] else 'No'}")
                st.write(f"**Skills:** {', '.join(alumni['skills'][:3])}")
            
            if st.button(f"Request Referral from {alumni['name']}", key=f"referral_{i}"):
                st.success(f"Referral request sent to {alumni['name']}! 🎉")
    
    # Save sample data to database if available
    if db_client and st.button("💾 Save Demo Alumni to Database"):
        try:
            for alumni in alumni_data:
                alumni["alumni_id"] = f"alumni_{alumni['name'].replace(' ', '_').lower()}"
                alumni["years_of_experience"] = 2024 - alumni["graduation_year"]
                alumni["created_at"] = datetime.now().isoformat()
            
            inserted_ids = db_client.insert_many_documents("alumni", alumni_data)
            st.success(f"✅ Saved {len(inserted_ids)} alumni profiles to database!")
        except Exception as e:
            st.error(f"Error saving to database: {e}")

def show_quick_demo():
    """Show quick demo functionality"""
    st.header("🚀 Quick Demo")
    
    st.info("This demo shows the core functionality of the Alumni Referrer Network Builder")
    
    # Simulated workflow
    st.subheader("1. Student Profile Analysis")
    demo_student = {
        "name": "Alex Smith",
        "major": "Computer Science",
        "skills": ["Python", "React", "AWS"],
        "target_company": "Google"
    }
    st.json(demo_student)
    
    st.subheader("2. Alumni Matching")
    if st.button("🔍 Find Matching Alumni"):
        with st.spinner("Analyzing alumni network..."):
            import time
            time.sleep(2)  # Simulate processing
            
            matches = [
                {"name": "Sarah Chen", "company": "Google", "compatibility": 0.95, "shared_skills": ["Python", "AWS"]},
                {"name": "David Kim", "company": "Google", "compatibility": 0.87, "shared_skills": ["React", "Python"]},
                {"name": "Lisa Wang", "company": "Google", "compatibility": 0.82, "shared_skills": ["AWS"]}
            ]
            
            st.success("✅ Found 3 highly compatible alumni!")
            
            for match in matches:
                with st.expander(f"{match['name']} - Compatibility: {match['compatibility']:.0%}"):
                    st.write(f"**Company:** {match['company']}")
                    st.write(f"**Shared Skills:** {', '.join(match['shared_skills'])}")
                    st.write(f"**Compatibility Score:** {match['compatibility']:.0%}")
    
    st.subheader("3. Referral Path Optimization")
    if st.button("🛤️ Generate Referral Strategy"):
        with st.spinner("Optimizing referral paths..."):
            import time
            time.sleep(1.5)
            
            strategy = {
                "primary_contact": "Sarah Chen",
                "approach": "Direct LinkedIn message",
                "success_probability": "85%",
                "estimated_response_time": "2-3 days"
            }
            
            st.success("✅ Optimal referral strategy generated!")
            st.json(strategy)
    
    st.subheader("4. Personalized Message Generation")
    if st.button("✉️ Generate Outreach Message"):
        with st.spinner("Creating personalized message..."):
            import time
            time.sleep(1)
            
            message = """Hi Sarah,

I hope this message finds you well. I'm Alex Smith, a Computer Science student graduating in 2025. I came across your profile and was impressed by your work at Google, particularly your experience with Python and AWS.

I'm very interested in opportunities at Google and would greatly appreciate any insights you might have about the company culture and the software engineering roles there. I noticed we share similar technical interests, especially in Python development and cloud technologies.

Would you be open to a brief conversation? I'd be happy to work around your schedule.

Thank you for your time and consideration.

Best regards,
Alex Smith"""
            
            st.success("✅ Personalized message generated!")
            st.text_area("Generated Message:", message, height=200)

if __name__ == "__main__":
    main()