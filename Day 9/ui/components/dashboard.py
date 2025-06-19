import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime, timedelta

def create_dashboard(data: Dict[str, List[Dict[str, Any]]]):
    """Create the main dashboard with visualizations"""
    
    students = data.get("students", [])
    alumni = data.get("alumni", [])
    referrals = data.get("referrals", [])
    companies = data.get("companies", [])
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Students", 
            value=len(students),
            delta=f"+{len([s for s in students if _is_recent(s.get('created_at'))])}" if students else None
        )
    
    with col2:
        st.metric(
            label="Alumni Network", 
            value=len(alumni),
            delta=f"+{len([a for a in alumni if _is_recent(a.get('created_at'))])}" if alumni else None
        )
    
    with col3:
        active_referrals = len([r for r in referrals if r.get('status') in ['pending', 'contacted']])
        st.metric(
            label="Active Referrals", 
            value=active_referrals,
            delta=f"{len(referrals) - active_referrals} completed"
        )
    
    with col4:
        success_rate = (len([r for r in referrals if r.get('status') == 'successful']) / len(referrals) * 100) if referrals else 0
        st.metric(
            label="Success Rate", 
            value=f"{success_rate:.1f}%",
            delta="↗️" if success_rate > 50 else "↘️"
        )
    
    # Charts section
    st.subheader("📊 Analytics Overview")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Alumni Distribution", "Referral Trends", "Student Insights", "Company Networks"])
    
    with tab1:
        _create_alumni_charts(alumni)
    
    with tab2:
        _create_referral_charts(referrals)
    
    with tab3:
        _create_student_charts(students)
    
    with tab4:
        _create_company_charts(alumni, companies)

def _create_alumni_charts(alumni: List[Dict[str, Any]]):
    """Create alumni-related charts"""
    if not alumni:
        st.info("No alumni data available for visualization.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Alumni by company
        companies = [a.get('current_company', 'Unknown') for a in alumni]
        company_counts = pd.Series(companies).value_counts().head(10)
        
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            title="Top 10 Companies by Alumni Count",
            labels={'x': 'Number of Alumni', 'y': 'Company'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Alumni by experience level
        experience_ranges = []
        for a in alumni:
            exp = a.get('years_of_experience', 0)
            if exp <= 2:
                experience_ranges.append('0-2 years')
            elif exp <= 5:
                experience_ranges.append('3-5 years')
            elif exp <= 10:
                experience_ranges.append('6-10 years')
            else:
                experience_ranges.append('10+ years')
        
        exp_counts = pd.Series(experience_ranges).value_counts()
        
        fig = px.pie(
            values=exp_counts.values,
            names=exp_counts.index,
            title="Alumni by Experience Level"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Skills analysis
    st.subheader("Popular Skills Among Alumni")
    all_skills = []
    for a in alumni:
        skills = a.get('skills', [])
        if isinstance(skills, list):
            all_skills.extend(skills)
        elif isinstance(skills, str):
            all_skills.extend(skills.split(', '))
    
    if all_skills:
        skill_counts = pd.Series(all_skills).value_counts().head(15)
        
        fig = px.bar(
            x=skill_counts.index,
            y=skill_counts.values,
            title="Top 15 Skills in Alumni Network",
            labels={'x': 'Skills', 'y': 'Frequency'}
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def _create_referral_charts(referrals: List[Dict[str, Any]]):
    """Create referral-related charts"""
    if not referrals:
        st.info("No referral data available for visualization.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Referral status distribution
        statuses = [r.get('status', 'unknown') for r in referrals]
        status_counts = pd.Series(statuses).value_counts()
        
        colors = {
            'successful': '#28a745',
            'pending': '#ffc107', 
            'contacted': '#17a2b8',
            'responded': '#6f42c1',
            'rejected': '#dc3545'
        }
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Referral Status Distribution",
            color=status_counts.index,
            color_discrete_map=colors
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Match scores distribution
        scores = [r.get('match_score', 0) for r in referrals if r.get('match_score')]
        
        if scores:
            fig = px.histogram(
                x=scores,
                nbins=20,
                title="Distribution of Match Scores",
                labels={'x': 'Match Score', 'y': 'Count'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No match score data available.")
    
    # Referral trends over time (if timestamp data is available)
    if referrals and any(r.get('created_at') for r in referrals):
        st.subheader("Referral Trends Over Time")
        
        # Create time series data
        dates = []
        for r in referrals:
            created_at = r.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        dates.append(datetime.fromisoformat(created_at.replace('Z', '+00:00')))
                    except:
                        dates.append(datetime.now())
                else:
                    dates.append(created_at)
        
        if dates:
            df = pd.DataFrame({'date': dates})
            df['date'] = pd.to_datetime(df['date'])
            df['count'] = 1
            
            # Group by day
            daily_counts = df.groupby(df['date'].dt.date)['count'].sum().reset_index()
            
            fig = px.line(
                daily_counts,
                x='date',
                y='count',
                title="Daily Referral Requests",
                labels={'date': 'Date', 'count': 'Number of Referrals'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def _create_student_charts(students: List[Dict[str, Any]]):
    """Create student-related charts"""
    if not students:
        st.info("No student data available for visualization.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Students by graduation year
        grad_years = [s.get('graduation_year', 2024) for s in students]
        year_counts = pd.Series(grad_years).value_counts().sort_index()
        
        fig = px.bar(
            x=year_counts.index,
            y=year_counts.values,
            title="Students by Graduation Year",
            labels={'x': 'Graduation Year', 'y': 'Number of Students'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Students by major
        majors = [s.get('major', 'Unknown') for s in students]
        major_counts = pd.Series(majors).value_counts().head(8)
        
        fig = px.pie(
            values=major_counts.values,
            names=major_counts.index,
            title="Students by Major"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Target companies analysis
    st.subheader("Popular Target Companies")
    all_targets = []
    for s in students:
        targets = s.get('target_companies', [])
        if isinstance(targets, list):
            all_targets.extend(targets)
        elif isinstance(targets, str):
            all_targets.extend(targets.split(', '))
    
    if all_targets:
        target_counts = pd.Series(all_targets).value_counts().head(10)
        
        fig = px.bar(
            x=target_counts.index,
            y=target_counts.values,
            title="Top 10 Target Companies",
            labels={'x': 'Company', 'y': 'Number of Students Interested'}
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def _create_company_charts(alumni: List[Dict[str, Any]], companies: List[Dict[str, Any]]):
    """Create company network charts"""
    if not alumni:
        st.info("No alumni data available for company analysis.")
        return
    
    # Company size analysis
    company_alumni_count = {}
    for a in alumni:
        company = a.get('current_company', 'Unknown')
        company_alumni_count[company] = company_alumni_count.get(company, 0) + 1
    
    # Network strength visualization
    st.subheader("Alumni Network Strength by Company")
    
    network_data = []
    for company, count in company_alumni_count.items():
        # Calculate network strength based on alumni count and diversity
        alumni_in_company = [a for a in alumni if a.get('current_company') == company]
        
        roles = set(a.get('current_role', '') for a in alumni_in_company)
        avg_experience = sum(a.get('years_of_experience', 0) for a in alumni_in_company) / len(alumni_in_company)
        
        network_strength = count * len(roles) * (avg_experience / 10)  # Composite score
        
        network_data.append({
            'company': company,
            'alumni_count': count,
            'role_diversity': len(roles),
            'avg_experience': avg_experience,
            'network_strength': network_strength
        })
    
    # Sort by network strength
    network_data.sort(key=lambda x: x['network_strength'], reverse=True)
    
    # Display top companies
    top_companies = network_data[:10]
    
    if top_companies:
        df = pd.DataFrame(top_companies)
        
        fig = px.scatter(
            df,
            x='alumni_count',
            y='avg_experience',
            size='network_strength',
            hover_name='company',
            hover_data=['role_diversity'],
            title="Company Network Analysis",
            labels={
                'alumni_count': 'Number of Alumni',
                'avg_experience': 'Average Experience (years)',
                'network_strength': 'Network Strength'
            }
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top companies table
        st.subheader("Top 10 Companies by Network Strength")
        display_df = df[['company', 'alumni_count', 'role_diversity', 'avg_experience', 'network_strength']].copy()
        display_df.columns = ['Company', 'Alumni Count', 'Role Diversity', 'Avg Experience', 'Network Strength']
        display_df['Network Strength'] = display_df['Network Strength'].round(2)
        display_df['Avg Experience'] = display_df['Avg Experience'].round(1)
        
        st.dataframe(display_df, use_container_width=True)

def _is_recent(timestamp, days=7):
    """Check if timestamp is within the last N days"""
    if not timestamp:
        return False
    
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        
        return dt > datetime.now() - timedelta(days=days)
    except:
        return False