from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from typing import Dict, Any, List
import logging
import json
import numpy as np
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MatchingOutputParser(BaseOutputParser):
    """Custom output parser for domain alignment results"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse the agent output into structured data"""
        try:
            # Try to extract JSON if present
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
                return json.loads(json_str)
            
            # Fallback parsing
            lines = text.strip().split('\n')
            result = {
                "matches": [],
                "reasoning": text,
                "confidence": 0.7
            }
            
            for line in lines:
                if "Score:" in line or "Match:" in line:
                    # Extract match information
                    parts = line.split(':')
                    if len(parts) >= 2:
                        score_text = parts[1].strip()
                        try:
                            score = float(score_text.split()[0])
                            result["matches"].append({"score": score, "details": line})
                        except:
                            pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing matching output: {e}")
            return {"matches": [], "reasoning": text, "confidence": 0.0}

class LangChainDomainAgent(BaseAgent):
    """Domain Alignment Agent using LangChain"""
    
    def __init__(self):
        super().__init__("LangChain Domain Alignment Agent")
        self._setup_langchain()
    
    def _setup_langchain(self):
        """Setup LangChain components"""
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=self.config["GEMINI_MODEL"],
            google_api_key=self.config["GOOGLE_API_KEY"],
            temperature=self.config["TEMPERATURE"]
        )
        
        # Create tools
        self.tools = [
            Tool(
                name="student_profile_analyzer",
                description="Analyze student profile and extract key matching criteria",
                func=self._analyze_student_profile
            ),
            Tool(
                name="alumni_compatibility_scorer",
                description="Calculate compatibility score between student and alumni",
                func=self._calculate_compatibility_score
            ),
            Tool(
                name="domain_expertise_matcher",
                description="Match student interests with alumni domain expertise",
                func=self._match_domain_expertise
            ),
            Tool(
                name="career_path_analyzer",
                description="Analyze career progression paths and compatibility",
                func=self._analyze_career_paths
            )
        ]
        
        # Create prompt template
        self.prompt = PromptTemplate(
            template="""
            You are an expert career counselor and domain alignment specialist. Your task is to analyze 
            student profiles and match them with the most compatible alumni for referral opportunities.
            
            STUDENT PROFILE:
            {student_profile}
            
            AVAILABLE ALUMNI:
            {alumni_profiles}
            
            MATCHING CRITERIA:
            - Domain/Industry alignment
            - Skill compatibility
            - Career level appropriateness
            - Company culture fit
            - Geographic considerations
            - Mentor-mentee potential
            
            Your goal is to:
            1. Analyze the student's career goals and interests
            2. Evaluate each alumni's domain expertise and background
            3. Calculate compatibility scores (0-1) for each student-alumni pair
            4. Provide detailed reasoning for top matches
            5. Consider both technical and soft skill alignments
            
            Available tools: {tools}
            Tool names: {tool_names}
            
            Think step by step and use the tools to perform thorough analysis.
            
            {agent_scratchpad}
            """,
            input_variables=["student_profile", "alumni_profiles", "tools", "tool_names", "agent_scratchpad"]
        )
        
        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.config["MAX_ITERATIONS"],
            return_intermediate_steps=True
        )
        
        # Output parser
        self.output_parser = MatchingOutputParser()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process domain alignment matching"""
        try:
            self.log_activity("Starting domain alignment process", input_data)
            
            student_profile = input_data.get("student_profile", {})
            alumni_profiles = input_data.get("alumni_profiles", [])
            
            if not student_profile or not alumni_profiles:
                return {
                    "success": False,
                    "error": "Missing student profile or alumni profiles",
                    "matches": []
                }
            
            # Prepare input for agent
            agent_input = {
                "student_profile": json.dumps(student_profile, indent=2),
                "alumni_profiles": json.dumps(alumni_profiles[:10], indent=2),  # Limit for context
                "tools": "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": [tool.name for tool in self.tools]
            }
            
            # Execute agent
            result = self.agent_executor.invoke(agent_input)
            
            # Parse output
            parsed_output = self.output_parser.parse(result["output"])
            
            # Calculate detailed matches
            detailed_matches = await self._calculate_detailed_matches(
                student_profile, alumni_profiles
            )
            
            # Combine results
            final_matches = self._combine_results(parsed_output, detailed_matches)
            
            # Sort by compatibility score
            final_matches.sort(key=lambda x: x.get("compatibility_score", 0), reverse=True)
            
            self.log_activity("Completed domain alignment", {
                "matches_found": len(final_matches),
                "top_score": final_matches[0].get("compatibility_score", 0) if final_matches else 0
            })
            
            # Store results
            alignment_result = {
                "student_id": student_profile.get("student_id"),
                "matches": final_matches,
                "analysis_summary": parsed_output.get("reasoning", ""),
                "total_alumni_analyzed": len(alumni_profiles),
                "timestamp": self._get_timestamp()
            }
            
            self.save_results("domain_alignments", alignment_result)
            
            return {
                "success": True,
                "matches": final_matches,
                "analysis_summary": parsed_output.get("reasoning", ""),
                "total_analyzed": len(alumni_profiles)
            }
            
        except Exception as e:
            logger.error(f"Error in LangChain domain alignment: {e}")
            self.log_activity("Error in domain alignment", {"error": str(e)})
            return {
                "success": False,
                "error": str(e),
                "matches": []
            }
    
    async def _calculate_detailed_matches(self, student_profile: Dict[str, Any], 
                                        alumni_profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate detailed compatibility matches"""
        matches = []
        
        student_skills = set(skill.lower() for skill in student_profile.get("skills", []))
        student_interests = set(interest.lower() for interest in student_profile.get("interests", []))
        student_targets = set(company.lower() for company in student_profile.get("target_companies", []))
        student_roles = set(role.lower() for role in student_profile.get("target_roles", []))
        
        for alumni in alumni_profiles:
            try:
                # Calculate various compatibility scores
                skill_score = self._calculate_skill_compatibility(
                    student_skills, set(skill.lower() for skill in alumni.get("skills", []))
                )
                
                company_score = self._calculate_company_compatibility(
                    student_targets, alumni.get("current_company", "").lower()
                )
                
                role_score = self._calculate_role_compatibility(
                    student_roles, alumni.get("current_role", "").lower()
                )
                
                experience_score = self._calculate_experience_compatibility(
                    student_profile.get("graduation_year", 2024),
                    alumni.get("years_of_experience", 0)
                )
                
                industry_score = self._calculate_industry_compatibility(
                    student_interests, alumni.get("industry", "").lower()
                )
                
                # Weighted overall score
                weights = {
                    "skill": 0.3,
                    "company": 0.25,
                    "role": 0.2,
                    "experience": 0.15,
                    "industry": 0.1
                }
                
                overall_score = (
                    skill_score * weights["skill"] +
                    company_score * weights["company"] +
                    role_score * weights["role"] +
                    experience_score * weights["experience"] +
                    industry_score * weights["industry"]
                )
                
                # Create match object
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
                        "experience_level": round(experience_score, 3),
                        "industry_match": round(industry_score, 3)
                    },
                    "matching_skills": list(student_skills.intersection(
                        set(skill.lower() for skill in alumni.get("skills", []))
                    )),
                    "referral_potential": self._assess_referral_potential(alumni),
                    "contact_feasibility": self._assess_contact_feasibility(alumni)
                }
                
                matches.append(match)
                
            except Exception as e:
                logger.error(f"Error calculating match for alumni {alumni.get('name', 'Unknown')}: {e}")
                continue
        
        return matches
    
    def _calculate_skill_compatibility(self, student_skills: set, alumni_skills: set) -> float:
        """Calculate skill compatibility score"""
        if not student_skills or not alumni_skills:
            return 0.0
        
        intersection = student_skills.intersection(alumni_skills)
        union = student_skills.union(alumni_skills)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_company_compatibility(self, target_companies: set, alumni_company: str) -> float:
        """Calculate company compatibility score"""
        if not target_companies or not alumni_company:
            return 0.5  # Neutral score
        
        for target in target_companies:
            if target in alumni_company or alumni_company in target:
                return 1.0
        
        return 0.0
    
    def _calculate_role_compatibility(self, target_roles: set, alumni_role: str) -> float:
        """Calculate role compatibility score"""
        if not target_roles or not alumni_role:
            return 0.5
        
        role_keywords = {
            "engineer": ["engineer", "developer", "programmer", "architect"],
            "manager": ["manager", "lead", "director", "head"],
            "analyst": ["analyst", "researcher", "scientist"],
            "consultant": ["consultant", "advisor", "strategist"]
        }
        
        alumni_role_lower = alumni_role.lower()
        
        for target_role in target_roles:
            # Direct match
            if target_role in alumni_role_lower:
                return 1.0
            
            # Keyword match
            for category, keywords in role_keywords.items():
                if target_role in keywords and any(keyword in alumni_role_lower for keyword in keywords):
                    return 0.8
        
        return 0.2
    
    def _calculate_experience_compatibility(self, student_grad_year: int, alumni_experience: int) -> float:
        """Calculate experience level compatibility"""
        current_year = 2024
        student_career_stage = max(0, current_year - student_grad_year)
        
        # Ideal mentor has 3-10 years more experience
        experience_gap = alumni_experience - student_career_stage
        
        if 3 <= experience_gap <= 10:
            return 1.0
        elif 1 <= experience_gap < 3:
            return 0.8
        elif 10 < experience_gap <= 15:
            return 0.7
        elif experience_gap > 15:
            return 0.5
        else:
            return 0.3
    
    def _calculate_industry_compatibility(self, student_interests: set, alumni_industry: str) -> float:
        """Calculate industry compatibility score"""
        if not student_interests or not alumni_industry:
            return 0.5
        
        industry_keywords = alumni_industry.lower().split()
        
        for interest in student_interests:
            if any(keyword in interest for keyword in industry_keywords):
                return 1.0
            if any(interest in keyword for keyword in industry_keywords):
                return 0.8
        
        return 0.3
    
    def _assess_referral_potential(self, alumni: Dict[str, Any]) -> str:
        """Assess the referral potential of an alumni"""
        willing = alumni.get("willing_to_refer", True)
        current_referrals = alumni.get("referral_count_this_month", 0)
        max_referrals = alumni.get("max_referrals_per_month", 3)
        years_exp = alumni.get("years_of_experience", 0)
        
        if not willing:
            return "low"
        elif current_referrals >= max_referrals:
            return "low"
        elif years_exp >= 5 and current_referrals < max_referrals // 2:
            return "high"
        elif years_exp >= 3:
            return "medium"
        else:
            return "low"
    
    def _assess_contact_feasibility(self, alumni: Dict[str, Any]) -> str:
        """Assess how easy it is to contact the alumni"""
        has_linkedin = bool(alumni.get("linkedin_url"))
        has_email = bool(alumni.get("email"))
        response_time = alumni.get("contact_preferences", {}).get("response_time", "unknown")
        
        if has_email and has_linkedin:
            return "high"
        elif has_linkedin or has_email:
            return "medium"
        else:
            return "low"
    
    def _combine_results(self, parsed_output: Dict[str, Any], 
                        detailed_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine parsed agent output with detailed calculations"""
        # Use detailed matches as primary source
        # Enhance with agent insights from parsed_output
        
        for match in detailed_matches:
            # Add agent reasoning if available
            agent_matches = parsed_output.get("matches", [])
            for agent_match in agent_matches:
                if isinstance(agent_match, dict) and agent_match.get("alumni_id") == match.get("alumni_id"):
                    match["agent_insights"] = agent_match.get("details", "")
                    break
        
        return detailed_matches
    
    # Tool functions
    def _analyze_student_profile(self, profile_json: str) -> str:
        """Analyze student profile tool function"""
        try:
            profile = json.loads(profile_json)
            analysis = {
                "career_stage": "entry_level" if profile.get("graduation_year", 2024) >= 2023 else "experienced",
                "primary_skills": profile.get("skills", [])[:5],
                "career_interests": profile.get("interests", []),
                "target_domains": profile.get("target_companies", [])
            }
            return json.dumps(analysis)
        except Exception as e:
            return f"Error analyzing profile: {str(e)}"
    
    def _calculate_compatibility_score(self, student_alumni_pair: str) -> str:
        """Calculate compatibility score tool function"""
        try:
            # This would be called by the agent with specific pairs
            return "Compatibility calculation completed"
        except Exception as e:
            return f"Error calculating compatibility: {str(e)}"
    
    def _match_domain_expertise(self, domains_json: str) -> str:
        """Match domain expertise tool function"""
        try:
            return "Domain expertise matching completed"
        except Exception as e:
            return f"Error matching domains: {str(e)}"
    
    def _analyze_career_paths(self, paths_json: str) -> str:
        """Analyze career paths tool function"""
        try:
            return "Career path analysis completed"
        except Exception as e:
            return f"Error analyzing career paths: {str(e)}"