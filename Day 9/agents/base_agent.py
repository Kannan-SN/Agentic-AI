from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import google.generativeai as genai
from config.settings import load_config
from database.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_name: str):
        """Initialize base agent"""
        self.agent_name = agent_name
        self.config = load_config()
        self.db_client = MongoDBClient()
        self.db_client.connect()
        
        # Configure Gemini
        genai.configure(api_key=self.config["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(self.config["GEMINI_MODEL"])
        
        logger.info(f"Initialized {agent_name} agent")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using Gemini"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config["TEMPERATURE"],
                    max_output_tokens=self.config["MAX_TOKENS"]
                )
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating response in {self.agent_name}: {e}")
            raise
    
    def log_activity(self, activity: str, data: Dict[str, Any] = None):
        """Log agent activity"""
        log_entry = {
            "agent": self.agent_name,
            "activity": activity,
            "data": data,
            "timestamp": self._get_timestamp()
        }
        
        try:
            self.db_client.insert_document("agent_logs", log_entry)
        except Exception as e:
            logger.error(f"Failed to log activity for {self.agent_name}: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def save_results(self, collection: str, data: Dict[str, Any]) -> str:
        """Save results to database"""
        try:
            return self.db_client.insert_document(collection, data)
        except Exception as e:
            logger.error(f"Failed to save results for {self.agent_name}: {e}")
            raise
    
    def get_data(self, collection: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve data from database"""
        try:
            return self.db_client.find_documents(collection, query)
        except Exception as e:
            logger.error(f"Failed to retrieve data for {self.agent_name}: {e}")
            raise
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple implementation - can be enhanced with more sophisticated methods
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction - can be enhanced with NLP libraries
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if'
        }
        
        words = text.lower().split()
        keywords = [word.strip('.,!?;:"()[]') for word in words 
                   if word.strip('.,!?;:"()[]') not in stop_words and len(word) > 2]
        
        return list(set(keywords))
    
    def close(self):
        """Close agent resources"""
        if self.db_client:
            self.db_client.close()
        logger.info(f"Closed {self.agent_name} agent")