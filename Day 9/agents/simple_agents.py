"""
Simplified AI agents that work without complex dependencies
"""

from typing import Dict, Any, List
import logging
import json
import random
from datetime import datetime
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SimpleCrewAgent(BaseAgent):
    """Simplified CrewAI Alumni Mining Agent"""
    
    def __init__(self):
        super().__init__("Simple CrewAI Alumni Agent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process alumni mining request"""
        try:
            self.log_activity("Starting simple alumni mining", input_data)
            
            target_companies = input_data.get("target_companies", [])
            graduation_years = input_data.get("graduation_years", [])
            role_filter = input_data.get("role_filter", [])
            skills_filter = input_data.get("skills_filter", [])
            
            # Generate sample alumni data
            alumni_data = self._generate_sample_alumni(target_companies, graduation_years, role_filter, skills_filter)
            
            # Store in database
            if alumni_data:
                self.db_client.insert_many_documents("alumni", alumni_data)
            
            self.log_activity("Completed alumni mining", {"alumni_count": len(alumni_data)})
            
            return {
                "success": True,
                "alumni_data": alumni_data,
                "total_found": len(alumni_data),
                "message": f"Successfully generated {len(alumni_data)} alumni profiles"
            }
            
        except Exception as e:
            logger.error(f"Error in simple crew agent: {e}")
            return {"success": False, "error": str(e), "alumni_data": []}
    
    def _generate_sample_alumni(self, companies: List[str], years: List[int], roles: List[str], skills: List[str]) -> List[Dict[str, Any]]:
        """Generate sample alumni data"""
        
        if not companies:
            companies = ["Google", "Microsoft", "Amazon", "Apple", "Meta"]
        if not roles:
            roles = ["Software Engineer", "Data Scientist", "Product Manager"]
        if not skills:
            skills = ["Python", "Java", "React", "AWS", "Machine Learning"]
        
        alumni_list = []
        num_alumni = random.randint(15, 25)
        
        first_names = ["Alex", "Sarah", "Michael", "Emily", "David", "Jessica", "Daniel", "Lisa", "Chris", "Amanda"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Wilson", "Moore"]
        
        for i in range(num_alumni):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            grad_year = random.choice(years) if years else random.randint(2015, 2023)
            
            alumni = {
                "alumni_id": f"alumni_{i+1}_{name.replace(' ', '_').lower()}",
                "name": name,
                "graduation_year": grad_year,
                "current_company": random.choice(companies),
                "current_role": random.choice(roles),
                "years_of_experience": 2024 - grad_year + random.randint(-1, 2),
                "skills": random.sample(skills, min(len(skills), random.randint(3, 6))),
                "industry": "Technology",
                "location": random.choice(["San Francisco, CA", "Seattle, WA", "New York, NY", "Austin, TX"]),
                "willing_to_refer": random.choice([True, True, True, False]),
                "max_referrals_per_month": random.randint(2, 5),
                "referral_count_this_month": random.randint(0, 2),
                "email": f"{name.lower().replace(' ', '.')}@company.com",
                "linkedin_url": f"https://linkedin.com/in/{name.lower().replace(' ', '-')}",
                "created_at": datetime.now().isoformat()
            }
            alumni_list.append(alumni)
        
        return alumni_list

class SimpleLangChainAgent(BaseAgent):
    """Simplified LangChain Domain Alignment Agent"""
    
    def __init__(self):
        super().__init__("Simple LangChain Domain Agent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process domain alignment"""
        try:
            self.log_activity("Starting domain alignment", input_data)
            
            student_profile = input_data.get("student_profile", {})
            alumni_profiles = input_data.get("alumni_profiles", [])
            
            if not student_profile or not alumni_profiles:
                return {"success": False, "error": "Missing required data", "matches": []}
            
            # Calculate matches
            matches = self._calculate_matches(student_profile, alumni_profiles)
            
            self.log_activity("Completed domain alignment", {"matches_found": len(matches)})
            
            return {
                "success": True,
                "matches": matches,
                "total_analyzed": len(alumni_profiles)
            }
            
        except Exception as e:
            logger.error(f"Error in simple langchain agent: {e}")
            return {"success": False, "error": str(e), "matches": []}
    
    def _calculate_matches(self, student: Dict[str, Any], alumni_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate compatibility matches"""
        matches = []
        
        student_skills = set(skill.lower() for skill in student.get("skills", []))
        student_companies = set(company.lower() for company in student.get("target_companies", []))
        student_roles = set(role.lower() for role in student.get("target_roles", []))
        
        for alumni in alumni_list:
            try:
                # Calculate compatibility scores
                skill_score = self._calculate_skill_match(student_skills, alumni.get("skills", []))
                company_score = self._calculate_company_match(student_companies, alumni.get("current_company", ""))
                role_score = self._calculate_role_match(student_roles, alumni.get("current_role", ""))
                experience_score = self._calculate_experience_match(student.get("graduation_year", 2024), alumni.get("years_of_experience", 0))
                
                # Overall compatibility
                overall_score = (skill_score * 0.4 + company_score * 0.3 + role_score * 0.2 + experience_score * 0.1)
                
                if overall_score > 0.3:  # Only include decent matches
                    match = {
                        "alumni_id": alumni.get("alumni_id"),
                        "alumni_name": alumni.get("name"),
                        "current_company": alumni.get("current_company"),
                        "current_role": alumni.get("current_role"),
                        "compatibility_score": round(overall_score, 3),
                        "score_breakdown": {
                            "skill_compatibility": round(skill_score, 3),
                            "company_alignment": round(company_score, 3),
                            "role_relevance": round(role_score, 3),
                            "experience_level": round(experience_score, 3)
                        },
                        "matching_skills": list(student_skills.intersection(set(skill.lower() for skill in alumni.get("skills", [])))),
                        "referral_potential": "high" if alumni.get("willing_to_refer", True) else "low"
                    }
                    matches.append(match)
                    
            except Exception as e:
                logger.error(f"Error processing alumni {alumni.get('name', 'Unknown')}: {e}")
                continue
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return matches[:15]  # Return top 15 matches
    
    def _calculate_skill_match(self, student_skills: set, alumni_skills: List[str]) -> float:
        """Calculate skill compatibility"""
        alumni_skills_set = set(skill.lower() for skill in alumni_skills)
        if not student_skills or not alumni_skills_set:
            return 0.3
        
        intersection = student_skills.intersection(alumni_skills_set)
        union = student_skills.union(alumni_skills_set)
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_company_match(self, target_companies: set, alumni_company: str) -> float:
        """Calculate company match"""
        if not target_companies:
            return 0.5
        
        alumni_company_lower = alumni_company.lower()
        return 1.0 if alumni_company_lower in target_companies else 0.2
    
    def _calculate_role_match(self, target_roles: set, alumni_role: str) -> float:
        """Calculate role match"""
        if not target_roles:
            return 0.5
        
        alumni_role_lower = alumni_role.lower()
        for target_role in target_roles:
            if target_role in alumni_role_lower or alumni_role_lower in target_role:
                return 1.0
        return 0.3
    
    def _calculate_experience_match(self, student_grad_year: int, alumni_experience: int) -> float:
        """Calculate experience level match"""
        ideal_gap = 3  # 3-7 years experience is ideal for mentoring
        actual_gap = alumni_experience
        
        if 3 <= actual_gap <= 7:
            return 1.0
        elif 1 <= actual_gap < 3:
            return 0.8
        elif 7 < actual_gap <= 12:
            return 0.7
        else:
            return 0.4

class SimpleLangGraphAgent(BaseAgent):
    """Simplified LangGraph Referral Path Agent"""
    
    def __init__(self):
        super().__init__("Simple LangGraph Referral Agent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process referral path generation"""
        try:
            self.log_activity("Starting referral path generation", input_data)
            
            student_profile = input_data.get("student_profile", {})
            matched_alumni = input_data.get("matched_alumni", [])
            
            if not matched_alumni:
                return {"success": False, "error": "No matched alumni provided", "recommendations": []}
            
            # Generate referral recommendations
            recommendations = self._generate_recommendations(student_profile, matched_alumni)
            
            self.log_activity("Completed referral path generation", {"recommendations_count": len(recommendations)})
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_paths": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error in simple langgraph agent: {e}")
            return {"success": False, "error": str(e), "recommendations": []}
    
    def _generate_recommendations(self, student: Dict[str, Any], matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate referral path recommendations"""
        recommendations = []
        
        for i, match in enumerate(matches[:8]):  # Top 8 matches
            try:
                # Create recommendation
                recommendation = {
                    "path_id": f"path_{i+1}",
                    "type": "direct",
                    "alumni_details": [match],
                    "score": match.get("compatibility_score", 0.5),
                    "success_probability": min(match.get("compatibility_score", 0.5) + 0.1, 1.0),
                    "connection_strength": match.get("compatibility_score", 0.5),
                    "estimated_response_time": self._estimate_response_time(match),
                    "path_description": f"Direct outreach to {match.get('alumni_name')} at {match.get('current_company')}",
                    "recommendation_rank": i + 1,
                    "confidence_level": self._calculate_confidence(match.get("compatibility_score", 0.5)),
                    "next_steps": [
                        "Research alumni's recent work and achievements",
                        "Craft personalized outreach message",
                        "Send LinkedIn connection request or email",
                        "Follow up if no response within a week"
                    ],
                    "action_plan": {
                        "immediate_actions": [
                            "Review alumni's LinkedIn profile",
                            "Identify shared connections or interests"
                        ],
                        "follow_up_actions": [
                            "Send personalized message",
                            "Schedule follow-up reminder"
                        ],
                        "timeline": "1-2 weeks for initial contact"
                    },
                    "evaluation": {
                        "accessibility": 0.8,
                        "influence": 0.7,
                        "responsiveness": 0.6,
                        "relevance": match.get("compatibility_score", 0.5),
                        "timing": 0.8
                    }
                }
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error creating recommendation {i}: {e}")
                continue
        
        return recommendations
    
    def _estimate_response_time(self, alumni: Dict[str, Any]) -> str:
        """Estimate response time based on alumni profile"""
        experience = alumni.get("years_of_experience", 0)
        role = alumni.get("current_role", "").lower()
        
        if "director" in role or "vp" in role or experience > 10:
            return "5-7 days"
        elif "manager" in role or "lead" in role or experience > 5:
            return "3-5 days"
        else:
            return "1-3 days"
    
    def _calculate_confidence(self, score: float) -> str:
        """Calculate confidence level"""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"

class SimpleAutoGenAgent(BaseAgent):
    """Simplified AutoGen Message Generator Agent"""
    
    def __init__(self):
        super().__init__("Simple AutoGen Message Agent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process message generation"""
        try:
            self.log_activity("Starting message generation", input_data)
            
            student_profile = input_data.get("student_profile", {})
            referral_recommendation = input_data.get("referral_recommendation", {})
            
            if not student_profile or not referral_recommendation:
                return {"success": False, "error": "Missing required data", "message_variations": []}
            
            # Generate message variations
            message_variations = self._generate_messages(student_profile, referral_recommendation)
            
            self.log_activity("Completed message generation", {"variations_count": len(message_variations)})
            
            return {
                "success": True,
                "message_variations": message_variations,
                "total_variations": len(message_variations),
                "recommended_approach": self._recommend_approach(message_variations)
            }
            
        except Exception as e:
            logger.error(f"Error in simple autogen agent: {e}")
            return {"success": False, "error": str(e), "message_variations": []}
    
    def _generate_messages(self, student: Dict[str, Any], referral: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate message variations"""
        alumni_details = referral.get("alumni_details", [{}])
        alumni = alumni_details[0] if alumni_details else {}
        
        student_name = student.get("name", "Student")
        alumni_name = alumni.get("alumni_name", alumni.get("name", "Alumni"))
        student_major = student.get("major", "Computer Science")
        alumni_company = alumni.get("current_company", "Company")
        alumni_role = alumni.get("current_role", "Professional")
        
        messages = []
        
        # LinkedIn message
        linkedin_msg = f"""Hi {alumni_name},

I hope this message finds you well. I'm {student_name}, a {student_major} student graduating in {student.get('graduation_year', 2025)}. I came across your profile and was impressed by your work at {alumni_company}.

I'm very interested in opportunities in your field and would greatly appreciate any insights you might have about {alumni_company} or the industry in general. Your experience as a {alumni_role} is exactly the kind of career path I'm hoping to pursue.

Would you be open to a brief conversation? I'd be happy to work around your schedule.

Thank you for your time and consideration.

Best regards,
{student_name}"""
        
        messages.append({
            "type": "linkedin",
            "description": "LinkedIn connection message",
            "content": linkedin_msg,
            "word_count": len(linkedin_msg.split()),
            "estimated_read_time": "1 min",
            "key_elements": ["Personal greeting", "Educational background", "Clear ask", "Professional closing"],
            "personalization_score": 0.85
        })
        
        # Email message
        email_msg = f"""Subject: {student_major} Student Seeking Career Guidance

Dear {alumni_name},

I hope this email finds you well. My name is {student_name}, and I'm a {student_major} student graduating in {student.get('graduation_year', 2025)}. I discovered your profile while researching professionals at {alumni_company}, and I was impressed by your career journey to your current role as {alumni_role}.

I'm currently seeking opportunities in the tech industry and would be incredibly grateful for any advice or insights you might be willing to share about your experience at {alumni_company} or the field in general.

I understand how valuable your time is, so I'd be happy to accommodate your schedule for a brief phone call or coffee meeting.

Thank you very much for considering my request.

Warm regards,
{student_name}
{student.get('email', 'student@university.edu')}"""
        
        messages.append({
            "type": "email",
            "description": "Professional email",
            "content": email_msg,
            "word_count": len(email_msg.split()),
            "estimated_read_time": "1-2 min",
            "key_elements": ["Email subject line", "Personal greeting", "Educational background", "Clear ask", "Contact information"],
            "personalization_score": 0.88
        })
        
        # Follow-up message
        followup_msg = f"""Hi {alumni_name},

I hope you're doing well. I wanted to follow up on my previous message about seeking career guidance.

I understand you must be very busy, but if you have just 10-15 minutes in the coming weeks, I would be incredibly grateful for any insights you could share about your experience at {alumni_company}.

Thank you again for your time and consideration.

Best regards,
{student_name}"""
        
        messages.append({
            "type": "followup",
            "description": "Follow-up message",
            "content": followup_msg,
            "word_count": len(followup_msg.split()),
            "estimated_read_time": "30 sec",
            "key_elements": ["Personal greeting", "Brief follow-up", "Time consideration", "Professional closing"],
            "personalization_score": 0.75
        })
        
        return messages
    
    def _recommend_approach(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recommend the best approach"""
        return {
            "primary": "linkedin",
            "alternative": "email",
            "reasoning": "LinkedIn is less formal and more appropriate for initial professional networking",
            "timing_advice": "Send on Tuesday-Thursday between 9 AM - 5 PM for best response rates",
            "follow_up_schedule": {
                "first_followup": "7 days after initial contact if no response",
                "second_followup": "14 days after initial contact",
                "thank_you": "Immediately after receiving response"
            }
        }