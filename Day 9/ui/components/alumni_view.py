import streamlit as st
import pandas as pd
from typing import List, Dict, Any

def create_alumni_view(alumni_data: List[Dict[str, Any]]):
    """Create alumni view component"""
    
    if not alumni_data:
        st.info("No alumni data to display.")
        return
    
    st.subheader(f"Alumni Network ({len(alumni_data)} profiles)")
    
    # Create DataFrame for better display
    df = pd.DataFrame(alumni_data)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unique_companies = df['current_company'].nunique() if 'current_company' in df.columns else 0
        st.metric("Companies", unique_companies)
    
    with col2:
        avg_experience = df['years_of_experience'].mean() if 'years_of_experience' in df.columns else 0
        st.metric("Avg Experience", f"{avg_experience:.1f} years")
    
    with col3:
        willing_to_refer = len([a for a in alumni_data if a.get('willing_to_refer', True)])
        st.metric("Willing to Refer", f"{willing_to_refer}/{len(alumni_data)}")
    
    with col4:
        avg_referrals = sum(a.get('max_referrals_per_month', 3) for a in alumni_data) / len(alumni_data)
        st.metric("Avg Monthly Capacity", f"{avg_referrals:.1f}")
    
    # Search and filter
    search_term = st.text_input("🔍 Search alumni", placeholder="Search by name, company, or skills...")
    
    # Filter alumni based on search
    if search_term:
        filtered_alumni = []
        for alumni in alumni_data:
            # Search in name, company, role, and skills
            search_fields = [
                alumni.get('name', ''),
                alumni.get('current_company', ''),
                alumni.get('current_role', ''),
                ', '.join(alumni.get('skills', [])) if isinstance(alumni.get('skills'), list) else str(alumni.get('skills', ''))
            ]
            
            if any(search_term.lower() in field.lower() for field in search_fields):
                filtered_alumni.append(alumni)
        
        alumni_data = filtered_alumni
        st.write(f"Found {len(alumni_data)} matching alumni")
    
    # Display options
    view_mode = st.radio("View Mode", ["Cards", "Table", "Detailed"], horizontal=True)
    
    if view_mode == "Cards":
        _display_alumni_cards(alumni_data)
    elif view_mode == "Table":
        _display_alumni_table(alumni_data)
    else:  # Detailed
        _display_alumni_detailed(alumni_data)

def _display_alumni_cards(alumni_data: List[Dict[str, Any]]):
    """Display alumni in card format"""
    
    # Display in columns
    cols_per_row = 2
    for i in range(0, len(alumni_data), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(alumni_data):
                alumni = alumni_data[i + j]
                
                with col:
                    with st.container():
                        # Header with name and company
                        st.markdown(f"### {alumni.get('name', 'Unknown')}")
                        st.markdown(f"**{alumni.get('current_role', 'Unknown Role')}** at **{alumni.get('current_company', 'Unknown Company')}**")
                        
                        # Experience and graduation
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📅 Graduated: {alumni.get('graduation_year', 'N/A')}")
                        with col2:
                            st.write(f"💼 Experience: {alumni.get('years_of_experience', 0)} years")
                        
                        # Skills
                        if alumni.get('skills'):
                            skills = alumni['skills']
                            if isinstance(skills, list):
                                skills_text = ', '.join(skills[:4])  # Show first 4 skills
                                if len(skills) > 4:
                                    skills_text += f" +{len(skills) - 4} more"
                            else:
                                skills_text = str(skills)[:50] + "..." if len(str(skills)) > 50 else str(skills)
                            
                            st.write(f"🛠️ **Skills:** {skills_text}")
                        
                        # Location and referral status
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📍 {alumni.get('location', 'Unknown')}")
                        with col2:
                            willing = alumni.get('willing_to_refer', True)
                            status_icon = "✅" if willing else "❌"
                            st.write(f"{status_icon} Referrals: {'Yes' if willing else 'No'}")
                        
                        # Contact info
                        if alumni.get('linkedin_url'):
                            st.markdown(f"[LinkedIn Profile]({alumni['linkedin_url']})")
                        
                        st.markdown("---")

def _display_alumni_table(alumni_data: List[Dict[str, Any]]):
    """Display alumni in table format"""
    
    if not alumni_data:
        return
    
    # Prepare data for table
    table_data = []
    for alumni in alumni_data:
        row = {
            'Name': alumni.get('name', 'Unknown'),
            'Company': alumni.get('current_company', 'Unknown'),
            'Role': alumni.get('current_role', 'Unknown'),
            'Experience': f"{alumni.get('years_of_experience', 0)} years",
            'Graduation': alumni.get('graduation_year', 'N/A'),
            'Location': alumni.get('location', 'Unknown'),
            'Willing to Refer': "Yes" if alumni.get('willing_to_refer', True) else "No",
            'Skills Count': len(alumni.get('skills', [])) if isinstance(alumni.get('skills'), list) else 0
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Alumni Data as CSV",
        data=csv,
        file_name="alumni_network.csv",
        mime="text/csv"
    )

def _display_alumni_detailed(alumni_data: List[Dict[str, Any]]):
    """Display alumni in detailed format"""
    
    if not alumni_data:
        return
    
    # Pagination
    items_per_page = 5
    total_pages = (len(alumni_data) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox("Page", range(1, total_pages + 1)) - 1
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(alumni_data))
        page_alumni = alumni_data[start_idx:end_idx]
    else:
        page_alumni = alumni_data
    
    for i, alumni in enumerate(page_alumni):
        with st.expander(f"{alumni.get('name', 'Unknown')} - {alumni.get('current_company', 'Unknown')}", expanded=i == 0):
            _display_single_alumni_detailed(alumni)

def _display_single_alumni_detailed(alumni: Dict[str, Any]):
    """Display a single alumni profile in detail"""
    
    # Basic Information
    st.subheader("Basic Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Name:** {alumni.get('name', 'Unknown')}")
        st.write(f"**Email:** {alumni.get('email', 'Not provided')}")
        st.write(f"**Graduation Year:** {alumni.get('graduation_year', 'N/A')}")
    
    with col2:
        st.write(f"**Current Company:** {alumni.get('current_company', 'Unknown')}")
        st.write(f"**Current Role:** {alumni.get('current_role', 'Unknown')}")
        st.write(f"**Years of Experience:** {alumni.get('years_of_experience', 0)}")
    
    with col3:
        st.write(f"**Industry:** {alumni.get('industry', 'Unknown')}")
        st.write(f"**Location:** {alumni.get('location', 'Unknown')}")
        st.write(f"**Degree:** {alumni.get('degree', 'N/A')}")
    
    # Skills
    if alumni.get('skills'):
        st.subheader("Skills")
        skills = alumni['skills']
        if isinstance(skills, list):
            # Display skills as tags
            skills_html = ""
            for skill in skills:
                skills_html += f'<span style="background-color: #f0f2f6; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 12px;">{skill}</span> '
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.write(skills)
    
    # Referral Information
    st.subheader("Referral Information")
    col1, col2 = st.columns(2)
    
    with col1:
        willing = alumni.get('willing_to_refer', True)
        st.write(f"**Willing to Refer:** {'✅ Yes' if willing else '❌ No'}")
        st.write(f"**Max Referrals per Month:** {alumni.get('max_referrals_per_month', 3)}")
    
    with col2:
        current_count = alumni.get('referral_count_this_month', 0)
        max_count = alumni.get('max_referrals_per_month', 3)
        st.write(f"**Current Month Referrals:** {current_count}/{max_count}")
        
        # Calculate availability
        availability = max_count - current_count
        if availability > 0:
            st.write(f"**Availability:** 🟢 {availability} slots available")
        else:
            st.write("**Availability:** 🔴 No slots available")
    
    # Contact Preferences
    if alumni.get('contact_preferences'):
        st.subheader("Contact Preferences")
        prefs = alumni['contact_preferences']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Preferred Method:** {prefs.get('method', 'Not specified')}")
        with col2:
            st.write(f"**Response Time:** {prefs.get('response_time', 'Not specified')}")
    
    # Company History
    if alumni.get('company_history'):
        st.subheader("Company History")
        for history in alumni['company_history']:
            st.write(f"• **{history.get('company', 'Unknown')}** - {history.get('role', 'Unknown Role')} ({history.get('duration', 'Unknown duration')})")
    
    # Contact Links
    st.subheader("Contact Information")
    links = []
    
    if alumni.get('linkedin_url'):
        links.append(f"[LinkedIn Profile]({alumni['linkedin_url']})")
    
    if alumni.get('email'):
        links.append(f"[Email](mailto:{alumni['email']})")
    
    if links:
        st.markdown(" | ".join(links))
    else:
        st.write("No contact information available")
    
    # Action buttons
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"Request Referral from {alumni.get('name', 'Alumni')}", key=f"referral_{alumni.get('alumni_id', 'unknown')}"):
            st.success("Referral request initiated! (This would trigger the referral process)")
    
    with col2:
        if st.button(f"Save to Favorites", key=f"favorite_{alumni.get('alumni_id', 'unknown')}"):
            st.info("Alumni saved to favorites!")
    
    with col3:
        if st.button(f"Share Profile", key=f"share_{alumni.get('alumni_id', 'unknown')}"):
            st.info("Profile sharing link generated!")

def create_alumni_comparison(alumni_list: List[Dict[str, Any]]):
    """Create a comparison view for selected alumni"""
    
    if len(alumni_list) < 2:
        st.warning("Select at least 2 alumni to compare.")
        return
    
    st.subheader(f"Alumni Comparison ({len(alumni_list)} profiles)")
    
    # Create comparison table
    comparison_data = []
    
    for alumni in alumni_list:
        row = {
            'Alumni': alumni.get('name', 'Unknown'),
            'Company': alumni.get('current_company', 'Unknown'),
            'Role': alumni.get('current_role', 'Unknown'),
            'Experience': alumni.get('years_of_experience', 0),
            'Graduation': alumni.get('graduation_year', 'N/A'),
            'Skills Count': len(alumni.get('skills', [])) if isinstance(alumni.get('skills'), list) else 0,
            'Willing to Refer': alumni.get('willing_to_refer', True),
            'Monthly Capacity': alumni.get('max_referrals_per_month', 3),
            'Current Usage': alumni.get('referral_count_this_month', 0),
            'Location': alumni.get('location', 'Unknown')
        }
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    # Skill comparison
    st.subheader("Skills Comparison")
    
    all_skills = set()
    for alumni in alumni_list:
        skills = alumni.get('skills', [])
        if isinstance(skills, list):
            all_skills.update(skills)
        elif isinstance(skills, str):
            all_skills.update(skills.split(', '))
    
    # Create skills matrix
    skills_matrix = []
    for skill in sorted(all_skills):
        row = {'Skill': skill}
        for alumni in alumni_list:
            alumni_skills = alumni.get('skills', [])
            if isinstance(alumni_skills, str):
                alumni_skills = alumni_skills.split(', ')
            
            has_skill = skill in alumni_skills if isinstance(alumni_skills, list) else False
            row[alumni.get('name', 'Unknown')] = '✅' if has_skill else '❌'
        
        skills_matrix.append(row)
    
    if skills_matrix:
        skills_df = pd.DataFrame(skills_matrix)
        st.dataframe(skills_df, use_container_width=True)
    
    # Recommendation
    st.subheader("Recommendation")
    
    # Simple scoring for recommendation
    scores = []
    for alumni in alumni_list:
        score = 0
        
        # Experience score (0-30)
        exp = alumni.get('years_of_experience', 0)
        score += min(exp * 3, 30)
        
        # Availability score (0-25)
        max_ref = alumni.get('max_referrals_per_month', 3)
        current_ref = alumni.get('referral_count_this_month', 0)
        availability = max_ref - current_ref
        score += (availability / max_ref) * 25 if max_ref > 0 else 0
        
        # Willingness score (0-20)
        if alumni.get('willing_to_refer', True):
            score += 20
        
        # Skills score (0-25)
        skill_count = len(alumni.get('skills', [])) if isinstance(alumni.get('skills'), list) else 0
        score += min(skill_count * 2, 25)
        
        scores.append({
            'Alumni': alumni.get('name', 'Unknown'),
            'Score': round(score, 1),
            'Recommendation': 'Highly Recommended' if score >= 80 else 'Recommended' if score >= 60 else 'Consider'
        })
    
    # Sort by score
    scores.sort(key=lambda x: x['Score'], reverse=True)
    
    score_df = pd.DataFrame(scores)
    st.dataframe(score_df, use_container_width=True)
    
    # Best choice highlight
    if scores:
        best_choice = scores[0]
        st.success(f"🏆 **Best Choice:** {best_choice['Alumni']} (Score: {best_choice['Score']}/100)")

def create_alumni_stats(alumni_data: List[Dict[str, Any]]):
    """Create alumni statistics dashboard"""
    
    if not alumni_data:
        st.info("No alumni data for statistics.")
        return
    
    st.subheader("Alumni Network Statistics")
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(alumni_data)
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_alumni = len(alumni_data)
        st.metric("Total Alumni", total_alumni)
    
    with col2:
        if 'current_company' in df.columns:
            unique_companies = df['current_company'].nunique()
            st.metric("Unique Companies", unique_companies)
        else:
            st.metric("Unique Companies", "N/A")
    
    with col3:
        willing_count = len([a for a in alumni_data if a.get('willing_to_refer', True)])
        willing_percentage = (willing_count / total_alumni) * 100 if total_alumni > 0 else 0
        st.metric("Willing to Refer", f"{willing_percentage:.1f}%")
    
    with col4:
        if 'years_of_experience' in df.columns:
            avg_exp = df['years_of_experience'].mean()
            st.metric("Avg Experience", f"{avg_exp:.1f} years")
        else:
            st.metric("Avg Experience", "N/A")
    
    # Charts
    tab1, tab2, tab3 = st.tabs(["Company Distribution", "Experience Levels", "Skills Analysis"])
    
    with tab1:
        if 'current_company' in df.columns:
            company_counts = df['current_company'].value_counts().head(10)
            st.bar_chart(company_counts)
        else:
            st.info("No company data available")
    
    with tab2:
        if 'years_of_experience' in df.columns:
            # Create experience level bins
            df['exp_level'] = pd.cut(df['years_of_experience'], 
                                   bins=[0, 2, 5, 10, float('inf')], 
                                   labels=['0-2 years', '3-5 years', '6-10 years', '10+ years'])
            exp_counts = df['exp_level'].value_counts()
            st.bar_chart(exp_counts)
        else:
            st.info("No experience data available")
    
    with tab3:
        # Skills analysis
        all_skills = []
        for alumni in alumni_data:
            skills = alumni.get('skills', [])
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                all_skills.extend(skills.split(', '))
        
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts().head(15)
            st.bar_chart(skill_counts)
        else:
            st.info("No skills data available")