from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from typing import Dict, Any, List
import logging
from agents.base_agent import BaseAgent
from services.linkedin_scraper import LinkedInScraper
from rag.rag_pipeline import RAGPipeline
import json

logger = logging.getLogger(__name__)

class LinkedInScrapingTool(BaseTool):
    """Custom tool for LinkedIn scraping"""
    name: str = "linkedin_scraper"
    description: str = "Scrapes LinkedIn profiles and company data for alumni information"
    
    def _run(self, query: str) -> str:
        """Execute LinkedIn scraping"""
        scraper = LinkedInScraper()
        results = scraper.search_alumni(query)
        return json.dumps(results)

class AlumniDataTool(BaseTool):
    """Custom tool for accessing alumni data"""
    name: str = "alumni_data_access"
    description: str = "Access and retrieve alumni data from the database"
    
    def __init__(self, db_client):
        super().__init__()
        self._db_client = db_client  # Use private attribute
    
    def _run(self, query: str) -> str:
        """Execute alumni data retrieval"""
        try:
            # Parse query to extract filters
            filters = self._parse_query(query)
            alumni_data = self._db_client.find_documents("alumni", filters)
            return json.dumps(alumni_data, default=str)
        except Exception as e:
            return f"Error retrieving alumni data: {str(e)}"
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into database filters"""
        filters = {}
        query_lower = query.lower()
        
        # Extract company names
        if "company" in query_lower:
            # Simple extraction - can be enhanced
            words = query.split()
            company_idx = words.index("company") if "company" in words else -1
            if company_idx >= 0 and company_idx < len(words) - 1:
                filters["current_company"] = {"$regex": words[company_idx + 1], "$options": "i"}
        
        # Extract graduation year
        if "year" in query_lower or "batch" in query_lower:
            import re
            years = re.findall(r'\b(19|20)\d{2}\b', query)
            if years:
                filters["graduation_year"] = int(years[0])
        
        return filters

class CrewAlumniAgent(BaseAgent):
    """Alumni Network Mining Agent using CrewAI with RAG"""
    
    def __init__(self):
        super().__init__("CrewAI Alumni Mining Agent")
        self.rag_pipeline = RAGPipeline()
        self.linkedin_scraper = LinkedInScraper()
        self._setup_crew()
    
    def _setup_crew(self):
        """Setup CrewAI agents and tasks"""
        
        # Tools
        self.tools = [
            LinkedInScrapingTool(),
            AlumniDataTool(self.db_client)
        ]
        
        # Alumni Research Agent
        self.research_agent = Agent(
            role="Alumni Research Specialist",
            goal="Find and extract comprehensive alumni data from LinkedIn and other sources",
            backstory="""You are an expert researcher specializing in alumni network analysis. 
            Your mission is to discover alumni working at target companies, extract their 
            professional information, and build comprehensive profiles for referral matching.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False
        )
        
        # Data Processing Agent
        self.processing_agent = Agent(
            role="Alumni Data Processor",
            goal="Process, validate, and enrich alumni data with additional context",
            backstory="""You are a data processing expert who ensures alumni information 
            is accurate, complete, and properly structured. You validate LinkedIn profiles, 
            extract key skills and experiences, and prepare data for referral matching.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False
        )
        
        # Company Intelligence Agent
        self.intelligence_agent = Agent(
            role="Company Intelligence Analyst",
            goal="Analyze company hiring patterns and alumni distribution",
            backstory="""You are a business intelligence analyst who understands company 
            hiring patterns, organizational structures, and how to identify the best 
            alumni contacts for referrals based on their roles and influence.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process alumni mining request"""
        try:
            self.log_activity("Starting alumni mining process", input_data)
            
            # Extract requirements
            target_companies = input_data.get("target_companies", [])
            graduation_years = input_data.get("graduation_years", [])
            skills_filter = input_data.get("skills_filter", [])
            role_filter = input_data.get("role_filter", [])
            
            # Create tasks
            research_task = Task(
                description=f"""Research alumni from graduation years {graduation_years} 
                currently working at companies: {target_companies}. 
                Focus on roles: {role_filter} and skills: {skills_filter}.
                Use LinkedIn scraping and database search to gather comprehensive data.""",
                agent=self.research_agent,
                expected_output="Comprehensive list of alumni with their current positions and contact information"
            )
            
            processing_task = Task(
                description="""Process and validate the researched alumni data. 
                Extract key information including current role, years of experience, 
                skills, and contact preferences. Enrich profiles with additional context.""",
                agent=self.processing_agent,
                expected_output="Clean, validated, and enriched alumni profiles ready for matching"
            )
            
            intelligence_task = Task(
                description="""Analyze the processed alumni data to identify the most 
                influential and accessible contacts for referrals. Consider their roles, 
                network positions, and referral potential.""",
                agent=self.intelligence_agent,
                expected_output="Ranked list of alumni with referral potential scores and contact strategies"
            )
            
            # Create and execute crew
            crew = Crew(
                agents=[self.research_agent, self.processing_agent, self.intelligence_agent],
                tasks=[research_task, processing_task, intelligence_task],
                verbose=True
            )
            
            # Execute crew
            result = crew.kickoff()
            
            # Process and store results
            alumni_data = self._process_crew_results(result, input_data)
            
            # Store in vector database for RAG
            await self._store_in_rag(alumni_data)
            
            self.log_activity("Completed alumni mining process", {"alumni_count": len(alumni_data)})
            
            return {
                "success": True,
                "alumni_data": alumni_data,
                "total_found": len(alumni_data),
                "message": f"Successfully mined {len(alumni_data)} alumni profiles"
            }
            
        except Exception as e:
            logger.error(f"Error in CrewAI alumni mining: {e}")
            self.log_activity("Error in alumni mining", {"error": str(e)})
            return {
                "success": False,
                "error": str(e),
                "alumni_data": [],
                "total_found": 0
            }
    
    def _process_crew_results(self, crew_result: str, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process crew execution results"""
        try:
            # Parse the crew result and extract alumni data
            alumni_profiles = []
            
            # The crew result contains the analysis - extract structured data
            lines = crew_result.split('\n')
            current_profile = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse alumni information from crew output
                if "Name:" in line:
                    if current_profile:
                        alumni_profiles.append(current_profile)
                    current_profile = {"name": line.replace("Name:", "").strip()}
                elif "Company:" in line:
                    current_profile["current_company"] = line.replace("Company:", "").strip()
                elif "Role:" in line:
                    current_profile["current_role"] = line.replace("Role:", "").strip()
                elif "LinkedIn:" in line:
                    current_profile["linkedin_url"] = line.replace("LinkedIn:", "").strip()
                elif "Skills:" in line:
                    skills = line.replace("Skills:", "").strip().split(",")
                    current_profile["skills"] = [s.strip() for s in skills]
                elif "Experience:" in line:
                    exp_text = line.replace("Experience:", "").strip()
                    try:
                        current_profile["years_of_experience"] = int(exp_text.split()[0])
                    except:
                        current_profile["years_of_experience"] = 0
            
            # Add the last profile
            if current_profile:
                alumni_profiles.append(current_profile)
            
            # Enrich profiles with additional data
            for profile in alumni_profiles:
                profile.update({
                    "alumni_id": f"alumni_{len(alumni_profiles)}_{profile.get('name', '').replace(' ', '_').lower()}",
                    "graduation_year": input_data.get("graduation_years", [2020])[0] if input_data.get("graduation_years") else 2020,
                    "degree": "Computer Science",  # Default - should be extracted
                    "major": "Technology",  # Default - should be extracted
                    "industry": "Technology",
                    "location": "Unknown",
                    "willing_to_refer": True,
                    "max_referrals_per_month": 3,
                    "referral_count_this_month": 0,
                    "company_history": [],
                    "contact_preferences": {"method": "linkedin", "response_time": "1-3 days"}
                })
            
            # Store in database
            if alumni_profiles:
                self.db_client.insert_many_documents("alumni", alumni_profiles)
            
            return alumni_profiles
            
        except Exception as e:
            logger.error(f"Error processing crew results: {e}")
            return []
    
    async def _store_in_rag(self, alumni_data: List[Dict[str, Any]]):
        """Store alumni data in RAG vector database"""
        try:
            for alumni in alumni_data:
                # Create document text for embedding
                doc_text = f"""
                Name: {alumni.get('name', '')}
                Company: {alumni.get('current_company', '')}
                Role: {alumni.get('current_role', '')}
                Skills: {', '.join(alumni.get('skills', []))}
                Experience: {alumni.get('years_of_experience', 0)} years
                Industry: {alumni.get('industry', '')}
                Graduation Year: {alumni.get('graduation_year', '')}
                """
                
                # Store in RAG pipeline
                await self.rag_pipeline.add_document(
                    doc_text, 
                    metadata={
                        "type": "alumni_profile",
                        "alumni_id": alumni.get("alumni_id"),
                        "company": alumni.get("current_company"),
                        "role": alumni.get("current_role")
                    }
                )
                
        except Exception as e:
            logger.error(f"Error storing alumni data in RAG: {e}")
    
    def search_alumni_with_rag(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search alumni using RAG pipeline"""
        try:
            return self.rag_pipeline.search(query, limit)
        except Exception as e:
            logger.error(f"Error searching alumni with RAG: {e}")
            return []