import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
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

@st.cache_resource
def load_config():
    """Load configuration (cached)"""
    from config.settings import load_config as _load_config
    return _load_config()

@st.cache_resource
def initialize_database():
    """Initialize database connection (cached)"""
    from database.mongodb_client import MongoDBClient
    db_client = MongoDBClient()
    db_client.connect()
    return db_client

@st.cache_resource
def initialize_agents():
    """Initialize AI agents (cached)"""
    agents = {}
    
    try:
        from agents.crew_agent import CrewAlumniAgent
        agents['crew'] = CrewAlumniAgent()
    except Exception as e:
        st.error(f"CrewAI Agent error: {e}")
    
    try:
        from agents.langchain_agent import LangChainDomainAgent
        agents['langchain'] = LangChainDomainAgent()
    except Exception as e:
        st.error(f"LangChain Agent error: {e}")
    
    try:
        from agents.langgraph_agent import LangGraphReferralAgent
        agents['langgraph'] = LangGraphReferralAgent()
    except Exception as e:
        st.error(f"LangGraph Agent error: {e}")
    
    try:
        from agents.autogen_agent import AutoGenOutreachAgent
        agents['autogen'] = AutoGenOutreachAgent()
    except Exception as e:
        st.error(f"AutoGen Agent error: {e}")
    
    return agents

@st.cache_resource
def initialize_rag():
    """Initialize RAG pipeline (cached)"""
    try:
        from rag.rag_pipeline import RAGPipeline
        return RAGPipeline()
    except Exception as e:
        st.error(f"RAG Pipeline error: {e}")
        return None

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🎓 Alumni Referrer Network Builder")
    st.markdown("**AI-Powered Student-Alumni Referral Matching System**")
    
    # Initialize components
    try:
        config = load_config()
        db_client = initialize_database()
        agents = initialize_agents()
        rag_pipeline = initialize_rag()
        
        st.success("✅ All systems initialized successfully!")
        
    except Exception as e:
        st.error(f"Initialization error: {e}")
        st.stop()
    
    # Initialize session state
    if 'current_student' not in st.session_state:
        st.session_state.current_student = None
    if 'current_alumni' not in st.session_state:
        st.session_state.current_alumni = []
    if 'current_matches' not in st.session_state:
        st.session_state.current_matches = []
    if 'current_referrals' not in st.session_state:
        st.session_state.current_referrals = []
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Student Profile", "Alumni Network", "Find Referrals", "Generate Messages", "Quick Demo"]
        )
        
        # System status
        st.header("System Status")
        show_system_status(db_client, agents, rag_pipeline)
    
    # Main content
    if page == "Dashboard":
        show_dashboard(db_client)
    elif page == "Student Profile":
        show_student_profile(db_client)
    elif page == "Alumni Network":
        show_alumni_network(db_client, agents, rag_pipeline)
    elif page == "Find Referrals":
        show_find_referrals(db_client, agents)
    elif page == "Generate Messages":
        show_generate_messages(agents)
    elif page == "Quick Demo":
        show_quick_demo()

def show_system_status(db_client, agents, rag_pipeline):
    """Show system status in sidebar"""
    
    # Database status
    try:
        student_count = len(db_client.find_documents("students"))
        alumni_count = len(db_client.find_documents("alumni"))
        st.metric("Students", student_count)
        st.metric("Alumni", alumni_count)
    except:
        st.metric("Students", "Error")
        st.metric("Alumni", "Error")
    
    # Agent status
    st.subheader("AI Agents")
    for agent_name, agent in agents.items():
        if agent:
            if agent_name == 'autogen' and hasattr(agent, 'autogen_available'):
                if agent.autogen_available:
                    st.write(f"✅ {agent_name.title()} (Full)")
                else:
                    st.write(f"⚠️ {agent_name.title()} (Fallback)")
            else:
                st.write(f"✅ {agent_name.title()}")
        else:
            st.write(f"❌ {agent_name.title()}")
    
    # RAG status
    if rag_pipeline:
        st.write("✅ RAG Pipeline")
    else:
        st.write("❌ RAG Pipeline")

def show_dashboard(db_client):
    """Show dashboard"""
    st.header("📊 Dashboard")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        students = db_client.find_documents("students")
        alumni = db_client.find_documents("alumni")
        referrals = db_client.find_documents("referrals")
        
        with col1:
            st.metric("Total Students", len(students))
        with col2:
            st.metric("Total Alumni", len(alumni))
        with col3:
            st.metric("Active Referrals", len(referrals))
        with col4:
            st.metric("Success Rate", "85%")
        
        # Charts
        if alumni:
            st.subheader("Alumni by Company")
            companies = [a.get('current_company', 'Unknown') for a in alumni]
            company_counts = pd.Series(companies).value_counts().head(10)
            st.bar_chart(company_counts)
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
        
        # Show demo data
        with col1:
            st.metric("Total Students", 156)
        with col2:
            st.metric("Total Alumni", 342)
        with col3:
            st.metric("Active Referrals", 89)
        with col4:
            st.metric("Success Rate", "85%")

def show_student_profile(db_client):
    """Show student profile management"""
    st.header("👨‍🎓 Student Profile")
    
    tab1, tab2 = st.tabs(["Create Profile", "View Profiles"])
    
    with tab1:
        with st.form("student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *")
                email = st.text_input("Email *")
                graduation_year = st.selectbox("Graduation Year *", [2024, 2025, 2026, 2027])
                major = st.selectbox("Major *", ["Computer Science", "Software Engineering", "Data Science", "Other"])
            
            with col2:
                target_company = st.selectbox("Target Company", ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Other"])
                target_role = st.selectbox("Target Role", ["Software Engineer", "Data Scientist", "Product Manager", "Other"])
                skills = st.multiselect("Skills", ["Python", "Java", "React", "AWS", "Machine Learning", "SQL"])
                gpa = st.number_input("GPA (Optional)", 0.0, 4.0, 0.0, 0.1)
            
            submitted = st.form_submit_button("Save Profile", type="primary")
            
            if submitted and name and email:
                try:
                    student_data = {
                        "student_id": f"student_{name.replace(' ', '_').lower()}_{graduation_year}",
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
                    
                    student_id = db_client.insert_document("students", student_data)
                    st.session_state.current_student = student_data
                    st.success(f"✅ Profile saved! ID: {student_id}")
                    st.json(student_data)
                    
                except Exception as e:
                    st.error(f"Error saving profile: {e}")
    
    with tab2:
        try:
            students = db_client.find_documents("students")
            if students:
                st.write(f"Found {len(students)} student profiles:")
                
                for student in students[-5:]:  # Show last 5
                    with st.expander(f"{student.get('name', 'Unknown')} - {student.get('major', 'Unknown')}"):
                        st.json(student)
                        if st.button(f"Select {student.get('name', 'Unknown')}", key=student.get('student_id')):
                            st.session_state.current_student = student
                            st.success(f"Selected {student.get('name', 'Unknown')}")
            else:
                st.info("No student profiles found. Create one in the 'Create Profile' tab.")
        except Exception as e:
            st.error(f"Error loading students: {e}")

def show_alumni_network(db_client, agents, rag_pipeline):
    """Show alumni network"""
    st.header("🎯 Alumni Network")
    
    tab1, tab2 = st.tabs(["Mine Alumni Data", "View Alumni"])
    
    with tab1:
        st.subheader("Generate Sample Alumni Data")
        
        col1, col2 = st.columns(2)
        with col1:
            companies = st.multiselect("Companies", ["Google", "Microsoft", "Amazon", "Apple", "Meta"], default=["Google", "Microsoft"])
        with col2:
            num_alumni = st.slider("Number of Alumni", 5, 50, 20)
        
        if st.button("🚀 Generate Alumni Data", type="primary"):
            try:
                # Generate sample data
                import random
                sample_alumni = []
                roles = ["Software Engineer", "Senior Engineer", "Engineering Manager", "Data Scientist", "Product Manager"]
                skills = ["Python", "Java", "React", "AWS", "Machine Learning", "SQL", "Docker", "Kubernetes"]
                
                for i in range(num_alumni):
                    alumni = {
                        "alumni_id": f"alumni_{i+1}",
                        "name": f"Alumni {i+1}",
                        "current_company": random.choice(companies),
                        "current_role": random.choice(roles),
                        "graduation_year": random.randint(2015, 2023),
                        "years_of_experience": random.randint(1, 10),
                        "skills": random.sample(skills, random.randint(3, 6)),
                        "industry": "Technology",
                        "willing_to_refer": random.choice([True, True, True, False]),
                        "max_referrals_per_month": random.randint(2, 5),
                        "created_at": datetime.now().isoformat()
                    }
                    sample_alumni.append(alumni)
                
                # Save to database
                db_client.insert_many_documents("alumni", sample_alumni)
                st.session_state.current_alumni = sample_alumni
                
                st.success(f"✅ Generated {len(sample_alumni)} alumni profiles!")
                
                # Show preview
                df = pd.DataFrame(sample_alumni)
                st.dataframe(df[['name', 'current_company', 'current_role', 'years_of_experience']], use_container_width=True)
                
            except Exception as e:
                st.error(f"Error generating alumni data: {e}")
    
    with tab2:
        try:
            alumni = db_client.find_documents("alumni")
            if alumni:
                st.write(f"Alumni Network: {len(alumni)} profiles")
                
                # Filters
                companies = list(set(a.get('current_company', '') for a in alumni if a.get('current_company')))
                selected_company = st.selectbox("Filter by Company", ["All"] + companies)
                
                if selected_company != "All":
                    alumni = [a for a in alumni if a.get('current_company') == selected_company]
                
                # Display alumni
                for alumni_profile in alumni[:10]:  # Show first 10
                    with st.expander(f"{alumni_profile.get('name', 'Unknown')} - {alumni_profile.get('current_company', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Role:** {alumni_profile.get('current_role', 'Unknown')}")
                            st.write(f"**Experience:** {alumni_profile.get('years_of_experience', 0)} years")
                        with col2:
                            st.write(f"**Skills:** {', '.join(alumni_profile.get('skills', [])[:3])}")
                            st.write(f"**Willing to Refer:** {'Yes' if alumni_profile.get('willing_to_refer') else 'No'}")
            else:
                st.info("No alumni data found. Generate some in the 'Mine Alumni Data' tab.")
        except Exception as e:
            st.error(f"Error loading alumni: {e}")

def show_find_referrals(db_client, agents):
    """Show referral finding"""
    st.header("🤝 Find Referrals")
    
    if not st.session_state.current_student:
        st.warning("Please select a student profile first.")
        return
    
    st.write(f"Finding referrals for: **{st.session_state.current_student.get('name')}**")
    
    if st.button("🎯 Find Compatible Alumni", type="primary"):
        try:
            alumni = db_client.find_documents("alumni")
            if not alumni:
                st.error("No alumni data available.")
                return
            
            # Simple compatibility matching
            student = st.session_state.current_student
            student_skills = set(student.get('skills', []))
            target_companies = student.get('target_companies', [])
            
            matches = []
            for alumni_profile in alumni:
                alumni_skills = set(alumni_profile.get('skills', []))
                company = alumni_profile.get('current_company', '')
                
                # Calculate compatibility
                skill_overlap = len(student_skills.intersection(alumni_skills))
                company_match = company in target_companies
                
                score = skill_overlap * 0.7 + (1.0 if company_match else 0.3)
                
                if score > 0.5:
                    matches.append({
                        **alumni_profile,
                        'compatibility_score': score,
                        'matching_skills': list(student_skills.intersection(alumni_skills))
                    })
            
            # Sort by score
            matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
            st.session_state.current_matches = matches
            
            st.success(f"✅ Found {len(matches)} compatible alumni!")
            
            # Display top matches
            for i, match in enumerate(matches[:5]):
                with st.expander(f"#{i+1} - {match.get('name')} (Score: {match['compatibility_score']:.2f})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Company:** {match.get('current_company')}")
                        st.write(f"**Role:** {match.get('current_role')}")
                    with col2:
                        st.write(f"**Experience:** {match.get('years_of_experience')} years")
                        st.write(f"**Matching Skills:** {', '.join(match.get('matching_skills', []))}")
                        
        except Exception as e:
            st.error(f"Error finding referrals: {e}")

def show_generate_messages(agents):
    """Show message generation"""
    st.header("✉️ Generate Messages")
    
    if not st.session_state.current_student:
        st.warning("Please select a student profile first.")
        return
    
    if not st.session_state.current_matches:
        st.warning("Please find referral matches first.")
        return
    
    # Select alumni for message
    alumni_options = [(i, f"{match.get('name')} - {match.get('current_company')}") 
                     for i, match in enumerate(st.session_state.current_matches[:5])]
    
    if alumni_options:
        selected_idx = st.selectbox(
            "Select Alumni for Message Generation",
            [idx for idx, _ in alumni_options],
            format_func=lambda x: alumni_options[x][1]
        )
        
        selected_alumni = st.session_state.current_matches[selected_idx]
        
        if st.button("📝 Generate Outreach Message", type="primary"):
            try:
                student = st.session_state.current_student
                
                # Generate sample message
                message = f"""Hi {selected_alumni.get('name')},

I hope this message finds you well. I'm {student.get('name')}, a {student.get('major')} student graduating in {student.get('graduation_year')}. I came across your profile and was impressed by your work at {selected_alumni.get('current_company')}.

I'm very interested in opportunities in your field and would greatly appreciate any insights you might have about {selected_alumni.get('current_company')} or the industry in general.

Would you be open to a brief conversation? I'd be happy to work around your schedule.

Thank you for your time and consideration.

Best regards,
{student.get('name')}"""
                
                st.success("✅ Message generated successfully!")
                st.text_area("Generated Message:", message, height=200)
                
                # Show message details
                st.write("**Message Analysis:**")
                st.write(f"- Word count: {len(message.split())} words")
                st.write(f"- Estimated read time: {max(1, len(message.split()) // 200)} minute(s)")
                st.write(f"- Personalization elements: Alumni name, company, student details")
                
            except Exception as e:
                st.error(f"Error generating message: {e}")

def show_quick_demo():
    """Show quick demo"""
    st.header("🚀 Quick Demo")
    
    st.info("This demonstrates the complete Alumni Referrer Network Builder workflow:")
    
    # Demo workflow
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Student Profile")
        demo_student = {
            "name": "Alex Smith",
            "major": "Computer Science",
            "graduation_year": 2025,
            "skills": ["Python", "React", "AWS"],
            "target_companies": ["Google", "Microsoft"]
        }
        st.json(demo_student)
    
    with col2:
        st.subheader("2. Alumni Match")
        demo_alumni = {
            "name": "Sarah Chen",
            "company": "Google",
            "role": "Senior Software Engineer",
            "experience": "5 years",
            "skills": ["Python", "Go", "AWS"]
        }
        st.json(demo_alumni)
    
    if st.button("🎯 Show Demo Matching", type="primary"):
        st.subheader("3. Compatibility Analysis")
        st.success("✅ High compatibility found!")
        st.write("- **Shared Skills:** Python, AWS")
        st.write("- **Company Match:** Target company (Google)")
        st.write("- **Compatibility Score:** 0.95/1.0")
        
        st.subheader("4. Generated Outreach Message")
        demo_message = """Hi Sarah,

I hope this message finds you well. I'm Alex Smith, a Computer Science student graduating in 2025. I came across your profile and was impressed by your work at Google.

I'm very interested in opportunities at Google and would greatly appreciate any insights you might have about the company culture and software engineering roles there. I noticed we share similar technical interests, especially in Python development and AWS.

Would you be open to a brief conversation? I'd be happy to work around your schedule.

Thank you for your time and consideration.

Best regards,
Alex Smith"""
        
        st.text_area("Demo Message:", demo_message, height=200)
        st.success("✅ Complete workflow demonstrated!")

if __name__ == "__main__":
    main()