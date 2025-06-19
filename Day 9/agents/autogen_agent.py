from typing import Dict, Any, List
import logging
import json
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Try to import AutoGen, fallback if not available
try:
    from autogen import ConversableAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    logger.warning("AutoGen not available, using fallback message generation")
    AUTOGEN_AVAILABLE = False

class AutoGenOutreachAgent(BaseAgent):
    """Outreach Message Generator Agent using AutoGen or fallback"""
    
    def __init__(self):
        super().__init__("AutoGen Outreach Message Generator")
        self.autogen_available = AUTOGEN_AVAILABLE
        if self.autogen_available:
            self._setup_autogen()
        else:
            logger.info("AutoGen not available, using built-in message templates")
    
    def _setup_autogen(self):
        """Setup AutoGen multi-agent system"""
        
        try:
            # Configuration for all agents
            llm_config = {
                "config_list": [{
                    "model": self.config["GEMINI_MODEL"],
                    "api_key": self.config["GOOGLE_API_KEY"],
                    "api_type": "google",
                }],
                "temperature": 0.7
            }
            
            # Message Strategist Agent
            self.strategist = ConversableAgent(
                name="MessageStrategist",
                system_message="""You are an expert communication strategist specializing in professional 
                networking and referral requests. Your role is to analyze the context and determine the 
                optimal messaging strategy for each referral outreach.
                
                Focus on:
                - Analyzing the relationship dynamics between student and alumni
                - Determining the appropriate tone and formality level
                - Identifying key value propositions and connection points
                - Suggesting optimal timing and follow-up strategies
                
                Always consider the alumni's perspective and what would motivate them to help.""",
                llm_config=llm_config,
                human_input_mode="NEVER",
            )
            
            # Content Writer Agent
            self.writer = ConversableAgent(
                name="ContentWriter",
                system_message="""You are a professional content writer specializing in personalized 
                outreach messages. Your role is to craft compelling, authentic, and professional messages 
                that feel personal and respectful.
                
                Your messages should:
                - Be concise yet comprehensive (150-300 words)
                - Include specific personal touches and shared connections
                - Clearly state the request without being pushy
                - Show genuine interest in the alumni's work and achievements
                - Include a clear call-to-action
                - Be grammatically perfect and professionally formatted
                
                Avoid generic templates - every message should feel uniquely crafted.""",
                llm_config=llm_config,
                human_input_mode="NEVER",
            )
            
            # Psychology Expert Agent
            self.psychologist = ConversableAgent(
                name="PsychologyExpert",
                system_message="""You are a behavioral psychology expert who understands motivation, 
                persuasion, and professional relationship dynamics. Your role is to ensure messages 
                are psychologically optimized for positive responses.
                
                Consider:
                - Reciprocity principles and how to create value for the alumni
                - Social proof and credibility indicators
                - The psychology of helping behavior
                - Cognitive biases that might affect response rates
                - Cultural sensitivity and professional norms
                
                Suggest improvements that make messages more compelling while maintaining authenticity.""",
                llm_config=llm_config,
                human_input_mode="NEVER",
            )
            
            # Quality Reviewer Agent
            self.reviewer = ConversableAgent(
                name="QualityReviewer",
                system_message="""You are a quality assurance expert who reviews professional 
                communications for excellence. Your role is to ensure every message meets the highest 
                standards of professionalism and effectiveness.
                
                Review for:
                - Grammar, spelling, and punctuation perfection
                - Appropriate tone and formality
                - Logical flow and structure
                - Completeness of information
                - Professional etiquette compliance
                - Potential misinterpretations or sensitivities
                
                Provide specific feedback and approve only when the message is excellent.""",
                llm_config=llm_config,
                human_input_mode="NEVER",
            )
            
            # Create group chat
            self.group_chat = GroupChat(
                agents=[self.strategist, self.writer, self.psychologist, self.reviewer],
                messages=[],
                max_round=15
            )
            
            # Group chat manager
            self.manager = GroupChatManager(
                groupchat=self.group_chat,
                llm_config=llm_config
            )
            
            logger.info("AutoGen agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup AutoGen: {e}")
            self.autogen_available = False
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process outreach message generation"""
        try:
            self.log_activity("Starting outreach message generation", input_data)
            
            student_profile = input_data.get("student_profile", {})
            referral_recommendation = input_data.get("referral_recommendation", {})
            
            if not student_profile or not referral_recommendation:
                return {
                    "success": False,
                    "error": "Missing student profile or referral recommendation",
                    "message_variations": []
                }
            
            # Extract alumni details
            alumni_details = referral_recommendation.get("alumni_details", [])
            if not alumni_details:
                return {
                    "success": False,
                    "error": "No alumni details in referral recommendation",
                    "message_variations": []
                }
            
            alumni = alumni_details[0]
            
            # Create context for message generation
            context = self._create_message_context(student_profile, alumni, referral_recommendation)
            
            # Generate message variations
            message_variations = []
            
            if self.autogen_available:
                # Use AutoGen for advanced message generation
                try:
                    message_variations = await self._generate_autogen_messages(context)
                except Exception as e:
                    logger.warning(f"AutoGen generation failed: {e}, falling back to templates")
                    message_variations = self._generate_template_messages(context)
            else:
                # Use template-based generation
                message_variations = self._generate_template_messages(context)
            
            self.log_activity("Completed outreach message generation", {
                "variations_created": len(message_variations),
                "total_word_count": sum(len(msg.get("content", "").split()) for msg in message_variations)
            })
            
            # Store results
            outreach_result = {
                "student_id": student_profile.get("student_id"),
                "alumni_id": alumni.get("alumni_id"),
                "referral_path_id": referral_recommendation.get("path_id"),
                "message_variations": message_variations,
                "context_used": context,
                "timestamp": self._get_timestamp()
            }
            
            self.save_results("outreach_messages", outreach_result)
            
            return {
                "success": True,
                "message_variations": message_variations,
                "total_variations": len(message_variations),
                "recommended_approach": self._recommend_approach(message_variations, referral_recommendation)
            }
            
        except Exception as e:
            logger.error(f"Error in AutoGen outreach message generation: {e}")
            self.log_activity("Error in outreach message generation", {"error": str(e)})
            return {
                "success": False,
                "error": str(e),
                "message_variations": []
            }
    
    async def _generate_autogen_messages(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate messages using AutoGen multi-agent system"""
        message_variations = []
        
        message_types = [
            ("linkedin", "LinkedIn connection message"),
            ("email", "Professional email"),
            ("followup", "Follow-up message"),
            ("thankyou", "Thank you message")
        ]
        
        for message_type, description in message_types:
            try:
                variation = await self._generate_message_variation(context, message_type, description)
                message_variations.append(variation)
            except Exception as e:
                logger.error(f"Failed to generate {message_type} message: {e}")
                # Fallback to template for this specific type
                fallback_msg = self._create_template_message(context, message_type, description)
                message_variations.append(fallback_msg)
        
        return message_variations
    
    def _generate_template_messages(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate messages using built-in templates"""
        message_variations = []
        
        message_types = [
            ("linkedin", "LinkedIn connection message"),
            ("email", "Professional email"),
            ("followup", "Follow-up message"),
            ("thankyou", "Thank you message")
        ]
        
        for message_type, description in message_types:
            variation = self._create_template_message(context, message_type, description)
            message_variations.append(variation)
        
        return message_variations
    
    def _create_template_message(self, context: Dict[str, Any], message_type: str, description: str) -> Dict[str, Any]:
        """Create a message using built-in templates"""
        student = context.get("student", {})
        alumni = context.get("alumni", {})
        relationship = context.get("relationship", {})
        
        # Personalization elements
        student_name = student.get("name", "Student")
        alumni_name = alumni.get("name", "Alumni")
        student_major = student.get("major", "Computer Science")
        alumni_company = alumni.get("current_company", "Company")
        alumni_role = alumni.get("current_role", "Professional")
        shared_skills = relationship.get("shared_skills", [])
        
        # Generate personalized content using Gemini
        try:
            prompt = f"""Create a professional {description} for a student reaching out to an alumni for referral.

Context:
- Student: {student_name}, studying {student_major}
- Alumni: {alumni_name}, {alumni_role} at {alumni_company}
- Shared skills: {', '.join(shared_skills[:3]) if shared_skills else 'technology'}
- Message type: {message_type}

Requirements:
- Professional but warm tone
- Mention specific shared connections or interests
- Clear but respectful ask for referral assistance
- 150-250 words
- Include appropriate greeting and closing for {message_type}

Generate only the message content, no explanations."""
            
            content = self.generate_response(prompt)
            
        except Exception as e:
            logger.error(f"Failed to generate AI content: {e}")
            # Use hardcoded template as final fallback
            content = self._get_hardcoded_template(message_type, context)
        
        return {
            "type": message_type,
            "description": description,
            "content": content,
            "word_count": len(content.split()),
            "estimated_read_time": f"{max(1, len(content.split()) // 200)} min",
            "key_elements": self._identify_key_elements(content),
            "personalization_score": self._calculate_personalization_score(content, context)
        }
    
    def _get_hardcoded_template(self, message_type: str, context: Dict[str, Any]) -> str:
        """Get hardcoded template as final fallback"""
        student = context.get("student", {})
        alumni = context.get("alumni", {})
        
        student_name = student.get("name", "Student Name")
        alumni_name = alumni.get("name", "Alumni Name")
        alumni_company = alumni.get("current_company", "Company")
        alumni_role = alumni.get("current_role", "Role")
        student_major = student.get("major", "Computer Science")
        
        templates = {
            "linkedin": f"""Hi {alumni_name},

I hope this message finds you well. I'm {student_name}, a {student_major} student graduating soon, and I came across your profile while researching professionals at {alumni_company}.

I'm very interested in opportunities in your field and would greatly appreciate any insights you might have about {alumni_company} or the industry in general. Your experience as a {alumni_role} is exactly the kind of career path I'm hoping to pursue.

Would you be open to a brief conversation? I'd be happy to work around your schedule.

Thank you for your time and consideration.

Best regards,
{student_name}""",
            
            "email": f"""Subject: {student_major} Student Seeking Career Guidance

Dear {alumni_name},

I hope this email finds you well. My name is {student_name}, and I'm a {student_major} student graduating soon. I discovered your profile while researching professionals at {alumni_company}, and I was impressed by your career journey to your current role as {alumni_role}.

I'm currently seeking opportunities in the tech industry and would be incredibly grateful for any advice or insights you might be willing to share about your experience at {alumni_company} or the field in general.

I understand how valuable your time is, so I'd be happy to accommodate your schedule for a brief phone call or coffee meeting.

Thank you very much for considering my request.

Warm regards,
{student_name}
[Contact Information]""",
            
            "followup": f"""Hi {alumni_name},

I hope you're doing well. I wanted to follow up on my previous message about seeking career guidance.

I understand you must be very busy, but if you have just 10-15 minutes in the coming weeks, I would be incredibly grateful for any insights you could share about your experience at {alumni_company}.

Thank you again for your time and consideration.

Best regards,
{student_name}""",
            
            "thankyou": f"""Dear {alumni_name},

Thank you so much for taking the time to speak with me and for your valuable insights about {alumni_company} and the industry. Your guidance was incredibly helpful and has given me a much clearer direction for my career path.

I truly appreciate your support and willingness to help. I'll keep you updated on my progress and hope to pay it forward someday.

With sincere gratitude,
{student_name}"""
        }
        
        return templates.get(message_type, "Thank you for your consideration.")
    
    async def _generate_message_variation(self, context: Dict[str, Any], 
                                        message_type: str, description: str) -> Dict[str, Any]:
        """Generate a specific message variation using AutoGen"""
        try:
            # Create the initial prompt
            prompt = f"""
            Create a {description} for the following scenario:
            
            CONTEXT:
            {json.dumps(context, indent=2)}
            
            MESSAGE TYPE: {message_type}
            
            Requirements:
            - Personalized and professional
            - Appropriate length for {message_type}
            - Include specific details about the student and alumni
            - Clear but respectful ask
            - Authentic tone
            
            Please work together to create the best possible message.
            """
            
            # Start the group chat conversation
            try:
                chat_result = self.strategist.initiate_chat(
                    self.manager,
                    message=prompt,
                    max_turns=8
                )
                
                # Extract the final message from chat result
                final_message = self._extract_final_message_from_result(chat_result, message_type)
                
            except Exception as e:
                logger.warning(f"AutoGen chat failed: {e}, using Gemini fallback")
                # Fallback to direct Gemini generation
                final_message = self._generate_with_gemini(context, message_type, description)
            
            return {
                "type": message_type,
                "description": description,
                "content": final_message,
                "word_count": len(final_message.split()),
                "estimated_read_time": f"{max(1, len(final_message.split()) // 200)} min",
                "key_elements": self._identify_key_elements(final_message),
                "personalization_score": self._calculate_personalization_score(final_message, context)
            }
            
        except Exception as e:
            logger.error(f"Error generating {message_type} message: {e}")
            # Final fallback to template
            return self._create_template_message(context, message_type, description)
    
    def _generate_with_gemini(self, context: Dict[str, Any], message_type: str, description: str) -> str:
        """Generate message directly with Gemini as AutoGen fallback"""
        try:
            student = context.get("student", {})
            alumni = context.get("alumni", {})
            relationship = context.get("relationship", {})
            
            prompt = f"""You are an expert in professional networking and career communications. 
            
            Create a {description} with these details:
            
            STUDENT:
            - Name: {student.get('name', 'Student')}
            - Major: {student.get('major', 'Computer Science')}
            - Graduation: {student.get('graduation_year', 2024)}
            - Skills: {', '.join(student.get('skills', [])[:5])}
            - Interests: {', '.join(student.get('interests', [])[:3])}
            
            ALUMNI:
            - Name: {alumni.get('name', 'Alumni')}
            - Company: {alumni.get('current_company', 'Company')}
            - Role: {alumni.get('current_role', 'Professional')}
            - Experience: {alumni.get('years_of_experience', 5)} years
            
            CONNECTION:
            - Shared skills: {', '.join(relationship.get('shared_skills', [])[:3])}
            - Connection strength: {relationship.get('connection_strength', 0.5):.2f}
            
            REQUIREMENTS for {message_type}:
            - Professional yet warm and authentic tone
            - 150-250 words
            - Specific mention of shared interests or connections
            - Clear but respectful referral request
            - Appropriate format for {message_type}
            - Include proper greeting and closing
            
            Generate ONLY the message content, no explanations or meta-text."""
            
            return self.generate_response(prompt)
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return self._get_hardcoded_template(message_type, context)
    
    def _extract_final_message_from_result(self, chat_result, message_type: str) -> str:
        """Extract the final approved message from chat result"""
        try:
            # Get the last message from the conversation
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                last_message = chat_result.chat_history[-1].get('content', '')
                
                # Look for message content in the response
                if any(starter in last_message.lower() for starter in ["subject:", "dear", "hi", "hello"]):
                    return last_message.strip()
            
            # If chat_result is a string, use it directly
            if isinstance(chat_result, str):
                return chat_result.strip()
            
            # Fallback: create a basic message if extraction fails
            return self._get_hardcoded_template(message_type, {})
            
        except Exception as e:
            logger.error(f"Error extracting message from result: {e}")
            return self._get_hardcoded_template(message_type, {})
    
    def _create_message_context(self, student_profile: Dict[str, Any], 
                              alumni: Dict[str, Any], 
                              referral_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive context for message generation"""
        
        # Extract shared connections and interests
        shared_skills = referral_recommendation.get("matching_skills", [])
        connection_type = referral_recommendation.get("type", "direct")
        
        # Build context
        context = {
            "student": {
                "name": student_profile.get("name", "Student"),
                "graduation_year": student_profile.get("graduation_year"),
                "degree": student_profile.get("degree"),
                "major": student_profile.get("major"),
                "skills": student_profile.get("skills", []),
                "interests": student_profile.get("interests", []),
                "target_companies": student_profile.get("target_companies", []),
                "target_roles": student_profile.get("target_roles", []),
                "gpa": student_profile.get("gpa"),
                "projects": student_profile.get("projects", []),
                "linkedin_url": student_profile.get("linkedin_url")
            },
            "alumni": {
                "name": alumni.get("name", "Alumni"),
                "graduation_year": alumni.get("graduation_year"),
                "current_company": alumni.get("current_company"),
                "current_role": alumni.get("current_role"),
                "years_of_experience": alumni.get("years_of_experience"),
                "skills": alumni.get("skills", []),
                "industry": alumni.get("industry"),
                "linkedin_url": alumni.get("linkedin_url")
            },
            "relationship": {
                "connection_type": connection_type,
                "shared_skills": shared_skills,
                "compatibility_score": referral_recommendation.get("compatibility_score"),
                "connection_strength": referral_recommendation.get("connection_strength"),
                "success_probability": referral_recommendation.get("success_probability"),
                "common_interests": referral_recommendation.get("personalization", {}).get("common_interests", []),
                "conversation_starters": referral_recommendation.get("personalization", {}).get("conversation_starters", [])
            },
            "company_context": {
                "is_target_company": alumni.get("current_company") in student_profile.get("target_companies", []),
                "company_name": alumni.get("current_company"),
                "role_relevance": alumni.get("current_role") in student_profile.get("target_roles", [])
            },
            "timing": {
                "alumni_referral_capacity": alumni.get("max_referrals_per_month", 3) - alumni.get("referral_count_this_month", 0),
                "estimated_response_time": referral_recommendation.get("estimated_response_time"),
                "best_contact_method": alumni.get("contact_preferences", {}).get("method", "linkedin")
            }
        }
        
        return context
    
    def _identify_key_elements(self, message: str) -> List[str]:
        """Identify key elements present in the message"""
        elements = []
        
        message_lower = message.lower()
        
        if "subject:" in message_lower:
            elements.append("Email subject line")
        
        if any(greeting in message_lower for greeting in ["dear", "hi", "hello"]):
            elements.append("Personal greeting")
        
        if "university" in message_lower or "graduate" in message_lower:
            elements.append("Educational background")
        
        if "experience" in message_lower or "work" in message_lower:
            elements.append("Work experience mention")
        
        if "appreciate" in message_lower or "grateful" in message_lower:
            elements.append("Gratitude expression")
        
        if "time" in message_lower and ("schedule" in message_lower or "convenient" in message_lower):
            elements.append("Scheduling consideration")
        
        if "?" in message:
            elements.append("Clear ask/question")
        
        if any(closing in message_lower for closing in ["regards", "sincerely", "thank you"]):
            elements.append("Professional closing")
        
        return elements
    
    def _calculate_personalization_score(self, message: str, context: Dict[str, Any]) -> float:
        """Calculate how personalized the message is"""
        score = 0.0
        message_lower = message.lower()
        
        # Check for personal details
        alumni_name = context.get("alumni", {}).get("name", "").lower()
        if alumni_name and alumni_name in message_lower:
            score += 0.2
        
        company = context.get("alumni", {}).get("current_company", "").lower()
        if company and company in message_lower:
            score += 0.2
        
        # Check for shared skills/interests
        shared_skills = context.get("relationship", {}).get("shared_skills", [])
        for skill in shared_skills:
            if skill.lower() in message_lower:
                score += 0.1
        
        # Check for specific role mention
        role = context.get("alumni", {}).get("current_role", "").lower()
        if role and role in message_lower:
            score += 0.15
        
        # Check for graduation year or university connection
        if "graduate" in message_lower or "university" in message_lower:
            score += 0.15
        
        # Check for specific request vs generic
        if "insights" in message_lower or "advice" in message_lower or "experience" in message_lower:
            score += 0.1
        
        # Check for consideration of alumni's time
        if "time" in message_lower and ("busy" in message_lower or "schedule" in message_lower):
            score += 0.1
        
        return min(score, 1.0)
    
    def _recommend_approach(self, message_variations: List[Dict[str, Any]], 
                          referral_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend the best approach based on the context"""
        
        connection_type = referral_recommendation.get("type", "direct")
        alumni_details = referral_recommendation.get("alumni_details", [])
        
        if not alumni_details:
            return {"primary": "email", "reasoning": "Default recommendation"}
        
        alumni = alumni_details[0]
        
        # Determine best primary approach
        primary_approach = "linkedin"  # Default
        reasoning = []
        
        # Check preferred contact method
        preferred_method = alumni.get("contact_preferences", {}).get("method", "linkedin")
        if preferred_method:
            primary_approach = preferred_method
            reasoning.append(f"Alumni prefers {preferred_method} contact")
        
        # Consider connection type
        if connection_type == "mutual_connection":
            primary_approach = "email"
            reasoning.append("Mutual connection referrals work better with formal email")
        
        # Consider seniority
        if alumni.get("years_of_experience", 0) >= 10:
            primary_approach = "email"
            reasoning.append("Senior professionals typically prefer email")
        
        # Find the matching message variation
        primary_message = next(
            (msg for msg in message_variations if msg.get("type") == primary_approach),
            message_variations[0] if message_variations else None
        )
        
        # Alternative approach
        alternative_approach = "email" if primary_approach == "linkedin" else "linkedin"
        alternative_message = next(
            (msg for msg in message_variations if msg.get("type") == alternative_approach),
            None
        )
        
        return {
            "primary": primary_approach,
            "primary_message": primary_message,
            "alternative": alternative_approach,
            "alternative_message": alternative_message,
            "reasoning": " | ".join(reasoning) if reasoning else "Standard approach",
            "timing_advice": self._get_timing_advice(referral_recommendation),
            "follow_up_schedule": self._create_followup_schedule()
        }
    
    def _get_timing_advice(self, referral_recommendation: Dict[str, Any]) -> str:
        """Get timing advice for outreach"""
        estimated_response = referral_recommendation.get("estimated_response_time", "3-5 days")
        
        if "1-3" in estimated_response:
            return "Send during business hours (9 AM - 5 PM) on Tuesday-Thursday for best response rates"
        elif "3-7" in estimated_response:
            return "Send early in the week (Monday-Tuesday) to allow for processing time"
        else:
            return "Send on Tuesday-Wednesday for optimal visibility in inbox"
    
    def _create_followup_schedule(self) -> Dict[str, str]:
        """Create follow-up schedule"""
        return {
            "first_followup": "7 days after initial contact if no response",
            "second_followup": "14 days after initial contact with different approach",
            "final_attempt": "21 days after initial contact with brief, gracious message",
            "thank_you": "Immediately after receiving any response or referral"
        }