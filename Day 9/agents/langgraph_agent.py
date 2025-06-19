from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import Dict, Any, List, TypedDict, Annotated
import logging
import json
from agents.base_agent import BaseAgent
import operator

logger = logging.getLogger(__name__)

class ReferralState(TypedDict):
    """State for referral path recommendation"""
    messages: Annotated[List[BaseMessage], operator.add]
    student_profile: Dict[str, Any]
    matched_alumni: List[Dict[str, Any]]
    referral_paths: List[Dict[str, Any]]
    current_analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    next_action: str

class LangGraphReferralAgent(BaseAgent):
    """Referral Path Recommender Agent using LangGraph"""
    
    def __init__(self):
        super().__init__("LangGraph Referral Path Agent")
        self._setup_langgraph()
    
    def _setup_langgraph(self):
        """Setup LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(ReferralState)
        
        # Add nodes
        workflow.add_node("analyze_connections", self._analyze_connections)
        workflow.add_node("build_paths", self._build_referral_paths)
        workflow.add_node("evaluate_paths", self._evaluate_paths)
        workflow.add_node("optimize_recommendations", self._optimize_recommendations)
        workflow.add_node("finalize_paths", self._finalize_paths)
        
        # Add edges
        workflow.add_edge("analyze_connections", "build_paths")
        workflow.add_edge("build_paths", "evaluate_paths")
        workflow.add_edge("evaluate_paths", "optimize_recommendations")
        workflow.add_edge("optimize_recommendations", "finalize_paths")
        workflow.add_edge("finalize_paths", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_connections")
        
        # Compile the graph
        self.app = workflow.compile()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process referral path recommendation"""
        try:
            self.log_activity("Starting referral path recommendation", input_data)
            
            # Initialize state
            initial_state = ReferralState(
                messages=[HumanMessage(content="Start referral path analysis")],
                student_profile=input_data.get("student_profile", {}),
                matched_alumni=input_data.get("matched_alumni", []),
                referral_paths=[],
                current_analysis={},
                recommendations=[],
                next_action="analyze_connections"
            )
            
            # Execute the workflow
            try:
                final_state = await self.app.ainvoke(initial_state)
            except Exception as e:
                logger.warning(f"Async invoke failed, trying sync: {e}")
                # Fallback to synchronous execution
                final_state = self.app.invoke(initial_state)
            
            # Extract results
            recommendations = final_state.get("recommendations", [])
            
            self.log_activity("Completed referral path recommendation", {
                "paths_generated": len(recommendations),
                "top_path_score": recommendations[0].get("score", 0) if recommendations else 0
            })
            
            # Store results
            referral_result = {
                "student_id": input_data.get("student_profile", {}).get("student_id"),
                "recommendations": recommendations,
                "total_paths_analyzed": len(final_state.get("referral_paths", [])),
                "timestamp": self._get_timestamp()
            }
            
            self.save_results("referral_paths", referral_result)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_paths": len(final_state.get("referral_paths", [])),
                "message": f"Generated {len(recommendations)} optimized referral paths"
            }
            
        except Exception as e:
            logger.error(f"Error in LangGraph referral path recommendation: {e}")
            self.log_activity("Error in referral path recommendation", {"error": str(e)})
            
            # Fallback: Generate simple recommendations
            fallback_recommendations = self._generate_fallback_recommendations(input_data)
            
            return {
                "success": True,  # Still return success with fallback
                "recommendations": fallback_recommendations,
                "total_paths": len(fallback_recommendations),
                "message": f"Generated {len(fallback_recommendations)} referral paths (fallback mode)",
                "warning": "Used fallback mode due to LangGraph execution error"
            }
    
    def _generate_fallback_recommendations(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback recommendations when LangGraph fails"""
        try:
            student_profile = input_data.get("student_profile", {})
            matched_alumni = input_data.get("matched_alumni", [])
            
            if not matched_alumni:
                return []
            
            recommendations = []
            
            for i, alumni in enumerate(matched_alumni[:8]):  # Top 8
                # Simple scoring based on compatibility
                base_score = alumni.get("compatibility_score", 0.5)
                
                # Adjust score based on various factors
                experience_bonus = min(alumni.get("years_of_experience", 0) / 20, 0.2)
                willing_bonus = 0.1 if alumni.get("willing_to_refer", True) else -0.1
                
                final_score = min(base_score + experience_bonus + willing_bonus, 1.0)
                
                recommendation = {
                    "path_id": f"fallback_path_{i+1}",
                    "type": "direct",
                    "alumni_details": [alumni],
                    "score": final_score,
                    "success_probability": min(final_score + 0.1, 1.0),
                    "connection_strength": alumni.get("compatibility_score", 0.5),
                    "estimated_response_time": "3-5 days",
                    "path_description": f"Direct contact with {alumni.get('alumni_name', 'alumni')} at {alumni.get('current_company', 'company')}",
                    "recommendation_rank": i + 1,
                    "confidence_level": "medium",
                    "next_steps": [
                        "Research alumni's recent work",
                        "Craft personalized message",
                        "Send connection request"
                    ],
                    "action_plan": {
                        "immediate_actions": ["Research alumni background", "Prepare outreach message"],
                        "follow_up_actions": ["Send follow-up if needed", "Thank for response"],
                        "timeline": "1-2 weeks"
                    }
                }
                
                recommendations.append(recommendation)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating fallback recommendations: {e}")
            return []
    
    def _analyze_connections(self, state: ReferralState) -> ReferralState:
        """Analyze potential connections and relationships"""
        try:
            student_profile = state["student_profile"]
            matched_alumni = state["matched_alumni"]
            
            connection_analysis = {
                "direct_connections": [],
                "mutual_connections": [],
                "company_networks": {},
                "skill_overlaps": {},
                "geographic_proximity": {}
            }
            
            # Analyze each alumni connection
            for alumni in matched_alumni:
                alumni_id = alumni.get("alumni_id")
                
                # Direct connection analysis
                direct_score = self._calculate_direct_connection_strength(student_profile, alumni)
                if direct_score > 0.5:
                    connection_analysis["direct_connections"].append({
                        "alumni_id": alumni_id,
                        "strength": direct_score,
                        "connection_type": "direct"
                    })
                
                # Company network analysis
                company = alumni.get("current_company", "")
                if company:
                    if company not in connection_analysis["company_networks"]:
                        connection_analysis["company_networks"][company] = []
                    connection_analysis["company_networks"][company].append(alumni_id)
                
                # Skill overlap analysis
                student_skills = set(student_profile.get("skills", []))
                alumni_skills = set(alumni.get("skills", []))
                overlap = student_skills.intersection(alumni_skills)
                if overlap:
                    connection_analysis["skill_overlaps"][alumni_id] = list(overlap)
            
            # Find mutual connections (alumni who know each other)
            connection_analysis["mutual_connections"] = self._find_mutual_connections(matched_alumni)
            
            # Update state
            state["current_analysis"] = connection_analysis
            state["messages"].append(AIMessage(content="Connection analysis completed"))
            
            return state
            
        except Exception as e:
            logger.error(f"Error in analyze_connections: {e}")
            state["messages"].append(AIMessage(content=f"Error in connection analysis: {str(e)}"))
            return state
    
    def _build_referral_paths(self, state: ReferralState) -> ReferralState:
        """Build potential referral paths"""
        try:
            connection_analysis = state["current_analysis"]
            matched_alumni = state["matched_alumni"]
            student_profile = state["student_profile"]
            
            referral_paths = []
            
            # Build direct paths
            for connection in connection_analysis.get("direct_connections", []):
                alumni_id = connection["alumni_id"]
                alumni = next((a for a in matched_alumni if a.get("alumni_id") == alumni_id), None)
                
                if alumni:
                    path = {
                        "path_id": f"direct_{alumni_id}",
                        "type": "direct",
                        "path": [student_profile.get("student_id"), alumni_id],
                        "alumni_details": [alumni],
                        "connection_strength": connection["strength"],
                        "estimated_response_time": self._estimate_response_time(alumni),
                        "success_probability": self._calculate_success_probability(alumni, "direct"),
                        "path_description": f"Direct contact with {alumni.get('name')} at {alumni.get('current_company')}"
                    }
                    referral_paths.append(path)
            
            # Build company-based paths
            for company, alumni_ids in connection_analysis.get("company_networks", {}).items():
                if len(alumni_ids) > 1:
                    # Multi-alumni company paths
                    company_alumni = [a for a in matched_alumni if a.get("alumni_id") in alumni_ids]
                    
                    # Sort by seniority/influence
                    company_alumni.sort(key=lambda x: x.get("years_of_experience", 0), reverse=True)
                    
                    for i, primary_alumni in enumerate(company_alumni[:3]):  # Top 3
                        path = {
                            "path_id": f"company_{company}_{i}",
                            "type": "company_network",
                            "path": [student_profile.get("student_id"), primary_alumni.get("alumni_id")],
                            "alumni_details": [primary_alumni],
                            "company": company,
                            "alternative_contacts": company_alumni[i+1:i+3],  # Next 2 as alternatives
                            "connection_strength": 0.7,  # Company-based connections are generally strong
                            "estimated_response_time": self._estimate_response_time(primary_alumni),
                            "success_probability": self._calculate_success_probability(primary_alumni, "company"),
                            "path_description": f"Contact {primary_alumni.get('name')} (senior contact) at {company}"
                        }
                        referral_paths.append(path)
            
            # Build mutual connection paths
            for mutual_pair in connection_analysis.get("mutual_connections", []):
                alumni_1 = next((a for a in matched_alumni if a.get("alumni_id") == mutual_pair[0]), None)
                alumni_2 = next((a for a in matched_alumni if a.get("alumni_id") == mutual_pair[1]), None)
                
                if alumni_1 and alumni_2:
                    # Choose the better intermediary
                    intermediary = alumni_1 if alumni_1.get("years_of_experience", 0) > alumni_2.get("years_of_experience", 0) else alumni_2
                    target = alumni_2 if intermediary == alumni_1 else alumni_1
                    
                    path = {
                        "path_id": f"mutual_{intermediary.get('alumni_id')}_{target.get('alumni_id')}",
                        "type": "mutual_connection",
                        "path": [student_profile.get("student_id"), intermediary.get("alumni_id"), target.get("alumni_id")],
                        "alumni_details": [intermediary, target],
                        "intermediary": intermediary,
                        "target": target,
                        "connection_strength": 0.8,  # Mutual connections are strong
                        "estimated_response_time": self._estimate_response_time(intermediary) + " + 1-2 days",
                        "success_probability": self._calculate_success_probability(target, "mutual"),
                        "path_description": f"Contact {target.get('name')} at {target.get('current_company')} through {intermediary.get('name')}"
                    }
                    referral_paths.append(path)
            
            # Build skill-based paths
            for alumni_id, shared_skills in connection_analysis.get("skill_overlaps", {}).items():
                if len(shared_skills) >= 3:  # Strong skill overlap
                    alumni = next((a for a in matched_alumni if a.get("alumni_id") == alumni_id), None)
                    
                    if alumni:
                        path = {
                            "path_id": f"skill_{alumni_id}",
                            "type": "skill_based",
                            "path": [student_profile.get("student_id"), alumni_id],
                            "alumni_details": [alumni],
                            "shared_skills": shared_skills,
                            "connection_strength": 0.6 + (len(shared_skills) * 0.1),
                            "estimated_response_time": self._estimate_response_time(alumni),
                            "success_probability": self._calculate_success_probability(alumni, "skill"),
                            "path_description": f"Connect with {alumni.get('name')} based on shared expertise in {', '.join(shared_skills[:3])}"
                        }
                        referral_paths.append(path)
            
            state["referral_paths"] = referral_paths
            state["messages"].append(AIMessage(content=f"Built {len(referral_paths)} potential referral paths"))
            
            return state
            
        except Exception as e:
            logger.error(f"Error in build_referral_paths: {e}")
            state["messages"].append(AIMessage(content=f"Error building paths: {str(e)}"))
            return state
    
    def _evaluate_paths(self, state: ReferralState) -> ReferralState:
        """Evaluate and score referral paths"""
        try:
            referral_paths = state["referral_paths"]
            
            for path in referral_paths:
                # Calculate comprehensive path score
                score = self._calculate_path_score(path)
                path["score"] = score
                
                # Add evaluation metrics
                path["evaluation"] = {
                    "accessibility": self._evaluate_accessibility(path),
                    "influence": self._evaluate_influence(path),
                    "responsiveness": self._evaluate_responsiveness(path),
                    "relevance": self._evaluate_relevance(path),
                    "timing": self._evaluate_timing(path)
                }
                
                # Calculate risk factors
                path["risk_factors"] = self._identify_risk_factors(path)
                
                # Generate path optimization suggestions
                path["optimization_suggestions"] = self._generate_optimization_suggestions(path)
            
            # Sort paths by score
            referral_paths.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            state["referral_paths"] = referral_paths
            state["messages"].append(AIMessage(content="Path evaluation completed"))
            
            return state
            
        except Exception as e:
            logger.error(f"Error in evaluate_paths: {e}")
            state["messages"].append(AIMessage(content=f"Error evaluating paths: {str(e)}"))
            return state
    
    def _optimize_recommendations(self, state: ReferralState) -> ReferralState:
        """Optimize and filter recommendations"""
        try:
            referral_paths = state["referral_paths"]
            student_profile = state["student_profile"]
            
            # Filter and optimize paths
            optimized_recommendations = []
            
            # Group paths by type for balanced recommendations
            path_groups = {}
            for path in referral_paths:
                path_type = path.get("type", "unknown")
                if path_type not in path_groups:
                    path_groups[path_type] = []
                path_groups[path_type].append(path)
            
            # Select best paths from each type
            max_per_type = {
                "direct": 3,
                "company_network": 2,
                "mutual_connection": 2,
                "skill_based": 1
            }
            
            for path_type, paths in path_groups.items():
                limit = max_per_type.get(path_type, 1)
                top_paths = sorted(paths, key=lambda x: x.get("score", 0), reverse=True)[:limit]
                
                for path in top_paths:
                    # Enhance path with optimization
                    optimized_path = self._optimize_individual_path(path, student_profile)
                    optimized_recommendations.append(optimized_path)
            
            # Final sorting and limiting
            optimized_recommendations.sort(key=lambda x: x.get("score", 0), reverse=True)
            final_recommendations = optimized_recommendations[:8]  # Top 8 recommendations
            
            # Add recommendation metadata
            for i, rec in enumerate(final_recommendations):
                rec["recommendation_rank"] = i + 1
                rec["confidence_level"] = self._calculate_confidence_level(rec)
                rec["next_steps"] = self._generate_next_steps(rec)
            
            state["recommendations"] = final_recommendations
            state["messages"].append(AIMessage(content=f"Generated {len(final_recommendations)} optimized recommendations"))
            
            return state
            
        except Exception as e:
            logger.error(f"Error in optimize_recommendations: {e}")
            state["messages"].append(AIMessage(content=f"Error optimizing recommendations: {str(e)}"))
            return state
    
    def _finalize_paths(self, state: ReferralState) -> ReferralState:
        """Finalize recommendations with actionable details"""
        try:
            recommendations = state["recommendations"]
            
            for rec in recommendations:
                # Add final actionable details
                rec["action_plan"] = self._create_action_plan(rec)
                rec["timeline"] = self._create_timeline(rec)
                rec["success_metrics"] = self._define_success_metrics(rec)
                rec["backup_plans"] = self._create_backup_plans(rec)
                
                # Generate final recommendation summary
                rec["summary"] = self._generate_recommendation_summary(rec)
            
            state["messages"].append(AIMessage(content="Finalized all referral path recommendations"))
            
            return state
            
        except Exception as e:
            logger.error(f"Error in finalize_paths: {e}")
            state["messages"].append(AIMessage(content=f"Error finalizing paths: {str(e)}"))
            return state
    
    # Helper methods
    def _calculate_direct_connection_strength(self, student: Dict[str, Any], alumni: Dict[str, Any]) -> float:
        """Calculate strength of direct connection"""
        score = 0.0
        
        # Same graduation year bonus
        if abs(student.get("graduation_year", 2024) - alumni.get("graduation_year", 2020)) <= 2:
            score += 0.3
        
        # Same degree/major bonus
        if student.get("major", "").lower() == alumni.get("major", "").lower():
            score += 0.2
        
        # Skill overlap
        student_skills = set(student.get("skills", []))
        alumni_skills = set(alumni.get("skills", []))
        skill_overlap = len(student_skills.intersection(alumni_skills))
        score += min(skill_overlap * 0.1, 0.3)
        
        # LinkedIn connection (if available)
        if alumni.get("linkedin_url"):
            score += 0.2
        
        return min(score, 1.0)
    
    def _find_mutual_connections(self, alumni_list: List[Dict[str, Any]]) -> List[tuple]:
        """Find alumni who might know each other"""
        mutual_connections = []
        
        for i in range(len(alumni_list)):
            for j in range(i + 1, len(alumni_list)):
                alumni_1 = alumni_list[i]
                alumni_2 = alumni_list[j]
                
                # Same company (current or previous)
                if alumni_1.get("current_company") == alumni_2.get("current_company"):
                    mutual_connections.append((alumni_1.get("alumni_id"), alumni_2.get("alumni_id")))
                
                # Similar graduation years
                if abs(alumni_1.get("graduation_year", 0) - alumni_2.get("graduation_year", 0)) <= 2:
                    mutual_connections.append((alumni_1.get("alumni_id"), alumni_2.get("alumni_id")))
        
        return mutual_connections
    
    def _estimate_response_time(self, alumni: Dict[str, Any]) -> str:
        """Estimate response time for alumni"""
        preferences = alumni.get("contact_preferences", {})
        response_time = preferences.get("response_time", "unknown")
        
        if response_time != "unknown":
            return response_time
        
        # Estimate based on role seniority
        role = alumni.get("current_role", "").lower()
        if "director" in role or "vp" in role or "head" in role:
            return "3-7 days"
        elif "manager" in role or "lead" in role:
            return "2-5 days"
        else:
            return "1-3 days"
    
    def _calculate_success_probability(self, alumni: Dict[str, Any], path_type: str) -> float:
        """Calculate probability of successful referral"""
        base_probability = {
            "direct": 0.6,
            "company": 0.7,
            "mutual": 0.8,
            "skill": 0.5
        }.get(path_type, 0.5)
        
        # Adjust based on alumni characteristics
        if alumni.get("willing_to_refer", True):
            base_probability += 0.1
        
        current_referrals = alumni.get("referral_count_this_month", 0)
        max_referrals = alumni.get("max_referrals_per_month", 3)
        
        if current_referrals < max_referrals:
            base_probability += 0.1
        elif current_referrals >= max_referrals:
            base_probability -= 0.2
        
        return min(base_probability, 1.0)
    
    def _calculate_path_score(self, path: Dict[str, Any]) -> float:
        """Calculate overall score for a referral path"""
        weights = {
            "connection_strength": 0.25,
            "success_probability": 0.25,
            "response_likelihood": 0.20,
            "influence_factor": 0.15,
            "accessibility": 0.15
        }
        
        connection_strength = path.get("connection_strength", 0.5)
        success_probability = path.get("success_probability", 0.5)
        
        # Calculate response likelihood
        response_time = path.get("estimated_response_time", "3-5 days")
        response_likelihood = 0.8 if "1-3" in response_time else 0.6
        
        # Calculate influence factor
        alumni_details = path.get("alumni_details", [])
        influence_factor = 0.5
        if alumni_details:
            alumni = alumni_details[0]
            years_exp = alumni.get("years_of_experience", 0)
            role = alumni.get("current_role", "").lower()
            
            if years_exp >= 10 or any(title in role for title in ["director", "vp", "head", "principal"]):
                influence_factor = 0.9
            elif years_exp >= 5 or "manager" in role or "lead" in role:
                influence_factor = 0.7
        
        # Calculate accessibility
        accessibility = 0.8 if path.get("type") == "direct" else 0.6
        
        # Weighted score
        score = (
            connection_strength * weights["connection_strength"] +
            success_probability * weights["success_probability"] +
            response_likelihood * weights["response_likelihood"] +
            influence_factor * weights["influence_factor"] +
            accessibility * weights["accessibility"]
        )
        
        return round(score, 3)
    
    def _evaluate_accessibility(self, path: Dict[str, Any]) -> float:
        """Evaluate how accessible the alumni is"""
        alumni_details = path.get("alumni_details", [])
        if not alumni_details:
            return 0.5
        
        alumni = alumni_details[0]
        score = 0.5
        
        if alumni.get("linkedin_url"):
            score += 0.2
        if alumni.get("email"):
            score += 0.2
        if alumni.get("willing_to_refer", True):
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_influence(self, path: Dict[str, Any]) -> float:
        """Evaluate the influence level of alumni"""
        alumni_details = path.get("alumni_details", [])
        if not alumni_details:
            return 0.5
        
        alumni = alumni_details[0]
        years_exp = alumni.get("years_of_experience", 0)
        role = alumni.get("current_role", "").lower()
        
        if years_exp >= 15 or any(title in role for title in ["vp", "director", "head", "principal"]):
            return 0.9
        elif years_exp >= 10 or any(title in role for title in ["senior", "lead", "manager"]):
            return 0.7
        elif years_exp >= 5:
            return 0.6
        else:
            return 0.4
    
    def _evaluate_responsiveness(self, path: Dict[str, Any]) -> float:
        """Evaluate likely responsiveness"""
        response_time = path.get("estimated_response_time", "unknown")
        
        if "1-3" in response_time:
            return 0.9
        elif "2-5" in response_time:
            return 0.7
        elif "3-7" in response_time:
            return 0.6
        else:
            return 0.5
    
    def _evaluate_relevance(self, path: Dict[str, Any]) -> float:
        """Evaluate relevance to student's goals"""
        # This would be enhanced with more context about student goals
        shared_skills = path.get("shared_skills", [])
        if shared_skills:
            return min(0.5 + len(shared_skills) * 0.1, 1.0)
        return 0.6
    
    def _evaluate_timing(self, path: Dict[str, Any]) -> float:
        """Evaluate timing appropriateness"""
        # Current month referral capacity
        alumni_details = path.get("alumni_details", [])
        if not alumni_details:
            return 0.5
        
        alumni = alumni_details[0]
        current_referrals = alumni.get("referral_count_this_month", 0)
        max_referrals = alumni.get("max_referrals_per_month", 3)
        
        if current_referrals == 0:
            return 1.0
        elif current_referrals < max_referrals / 2:
            return 0.8
        elif current_referrals < max_referrals:
            return 0.6
        else:
            return 0.2
    
    def _identify_risk_factors(self, path: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        alumni_details = path.get("alumni_details", [])
        if alumni_details:
            alumni = alumni_details[0]
            
            if not alumni.get("willing_to_refer", True):
                risks.append("Alumni may not be willing to provide referrals")
            
            if alumni.get("referral_count_this_month", 0) >= alumni.get("max_referrals_per_month", 3):
                risks.append("Alumni has reached referral limit for this month")
            
            if not alumni.get("linkedin_url") and not alumni.get("email"):
                risks.append("Limited contact information available")
        
        if path.get("type") == "mutual_connection":
            risks.append("Depends on intermediary's willingness to help")
        
        if path.get("success_probability", 0) < 0.5:
            risks.append("Lower probability of successful referral")
        
        return risks
    
    def _generate_optimization_suggestions(self, path: Dict[str, Any]) -> List[str]:
        """Generate suggestions to optimize the path"""
        suggestions = []
        
        if path.get("connection_strength", 0) < 0.6:
            suggestions.append("Research common connections or shared interests before reaching out")
        
        if "Limited contact information" in path.get("risk_factors", []):
            suggestions.append("Try to find mutual connections who can provide better contact details")
        
        if path.get("type") == "direct":
            suggestions.append("Personalize outreach message with specific details about their work")
        
        if path.get("success_probability", 0) < 0.7:
            suggestions.append("Consider timing the outreach for better response rates")
        
        return suggestions
    
    def _optimize_individual_path(self, path: Dict[str, Any], student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize individual path based on student profile"""
        # Add personalization based on student profile
        path["personalization"] = {
            "common_interests": self._find_common_interests(path, student_profile),
            "conversation_starters": self._generate_conversation_starters(path, student_profile),
            "value_proposition": self._create_value_proposition(path, student_profile)
        }
        
        return path
    
    def _find_common_interests(self, path: Dict[str, Any], student_profile: Dict[str, Any]) -> List[str]:
        """Find common interests between student and alumni"""
        alumni_details = path.get("alumni_details", [])
        if not alumni_details:
            return []
        
        alumni = alumni_details[0]
        student_skills = set(student_profile.get("skills", []))
        alumni_skills = set(alumni.get("skills", []))
        
        common_skills = list(student_skills.intersection(alumni_skills))
        
        # Add other potential common interests
        common_interests = common_skills.copy()
        
        if student_profile.get("major") == alumni.get("major"):
            common_interests.append(f"Both studied {student_profile.get('major')}")
        
        return common_interests[:5]  # Top 5
    
    def _generate_conversation_starters(self, path: Dict[str, Any], student_profile: Dict[str, Any]) -> List[str]:
        """Generate conversation starters"""
        alumni_details = path.get("alumni_details", [])
        if not alumni_details:
            return []
        
        alumni = alumni_details[0]
        starters = []
        
        # Skills-based starter
        shared_skills = path.get("shared_skills", [])
        if shared_skills:
            starters.append(f"I noticed we both have experience with {shared_skills[0]}")
        
        # Company-based starter
        if alumni.get("current_company") in student_profile.get("target_companies", []):
            starters.append(f"I'm very interested in opportunities at {alumni.get('current_company')}")
        
        # Role-based starter
        if alumni.get("current_role"):
            starters.append(f"I'd love to learn more about the {alumni.get('current_role')} role")
        
        return starters[:3]
    
    def _create_value_proposition(self, path: Dict[str, Any], student_profile: Dict[str, Any]) -> str:
        """Create value proposition for the student"""
        student_strengths = []
        
        if student_profile.get("gpa", 0) >= 3.5:
            student_strengths.append("strong academic performance")
        
        if len(student_profile.get("skills", [])) >= 5:
            student_strengths.append("diverse technical skills")
        
        if student_profile.get("projects"):
            student_strengths.append("hands-on project experience")
        
        if student_strengths:
            return f"Student brings {', '.join(student_strengths)} and strong motivation"
        else:
            return "Motivated student seeking mentorship and career guidance"
    
    def _calculate_confidence_level(self, recommendation: Dict[str, Any]) -> str:
        """Calculate confidence level for recommendation"""
        score = recommendation.get("score", 0)
        
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _generate_next_steps(self, recommendation: Dict[str, Any]) -> List[str]:
        """Generate next steps for the recommendation"""
        steps = []
        
        if recommendation.get("type") == "direct":
            steps.append("Research alumni's recent work and achievements")
            steps.append("Craft personalized outreach message")
            steps.append("Send connection request or email")
        elif recommendation.get("type") == "mutual_connection":
            steps.append("Contact intermediary alumni first")
            steps.append("Request introduction to target alumni")
            steps.append("Prepare background for intermediary to share")
        
        steps.append("Follow up if no response within a week")
        steps.append("Prepare for potential conversation or interview")
        
        return steps
    
    def _create_action_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed action plan"""
        return {
            "immediate_actions": self._generate_next_steps(recommendation)[:2],
            "follow_up_actions": self._generate_next_steps(recommendation)[2:],
            "preparation_required": [
                "Research company and role requirements",
                "Prepare elevator pitch",
                "Update resume if needed"
            ],
            "timeline": "1-2 weeks for initial contact, 2-4 weeks for referral process"
        }
    
    def _create_timeline(self, recommendation: Dict[str, Any]) -> Dict[str, str]:
        """Create timeline for referral process"""
        return {
            "day_1": "Research and prepare outreach",
            "day_2-3": "Send initial contact",
            "day_7-10": "Follow up if needed",
            "day_14-21": "Referral conversation/interview",
            "day_21-28": "Submit application with referral"
        }
    
    def _define_success_metrics(self, recommendation: Dict[str, Any]) -> Dict[str, str]:
        """Define success metrics"""
    def _define_success_metrics(self, recommendation: Dict[str, Any]) -> Dict[str, str]:
        """Define success metrics"""
        return {
            "response_rate": "Alumni responds within 7 days",
            "engagement": "Positive response to referral request",
            "referral_provided": "Alumni agrees to provide referral",
            "application_success": "Application moves to interview stage",
            "relationship_building": "Ongoing professional relationship established"
        }
    
    def _create_backup_plans(self, recommendation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create backup plans if primary path fails"""
        backups = []
        
        # Alternative contact method
        backups.append({
            "type": "alternative_contact",
            "description": "Try different contact method (LinkedIn vs email)",
            "trigger": "No response after 7 days"
        })
        
        # Alternative alumni
        if recommendation.get("alternative_contacts"):
            backups.append({
                "type": "alternative_alumni",
                "description": "Contact alternative alumni at same company",
                "trigger": "Primary contact declines or doesn't respond"
            })
        
        # Different approach
        backups.append({
            "type": "different_approach",
            "description": "Try informational interview approach instead of direct referral request",
            "trigger": "Referral request is declined"
        })
        
        return backups
    
    def _generate_recommendation_summary(self, recommendation: Dict[str, Any]) -> str:
        """Generate final recommendation summary"""
        alumni_details = recommendation.get("alumni_details", [])
        if not alumni_details:
            return "No alumni details available"
        
        alumni = alumni_details[0]
        path_type = recommendation.get("type", "unknown")
        score = recommendation.get("score", 0)
        
        summary = f"""
        Rank #{recommendation.get('recommendation_rank', 'N/A')} Recommendation (Score: {score:.2f})
        
        Contact: {alumni.get('name', 'Unknown')} at {alumni.get('current_company', 'Unknown Company')}
        Role: {alumni.get('current_role', 'Unknown Role')}
        Path Type: {path_type.replace('_', ' ').title()}
        
        Why this is a good match:
        - {recommendation.get('path_description', 'Strong professional connection')}
        - Success probability: {recommendation.get('success_probability', 0):.0%}
        - Expected response time: {recommendation.get('estimated_response_time', 'Unknown')}
        
        Confidence Level: {recommendation.get('confidence_level', 'medium').title()}
        """
        
        return summary.strip()