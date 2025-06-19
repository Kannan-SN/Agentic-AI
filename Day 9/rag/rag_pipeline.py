import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import json
import uuid
from pathlib import Path
from config.settings import load_config

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for alumni data"""
    
    def __init__(self):
        """Initialize RAG pipeline"""
        self.config = load_config()
        self._setup_embeddings()
        self._setup_vector_store()
    
    def _setup_embeddings(self):
        """Setup embedding model"""
        try:
            self.embedding_model = SentenceTransformer(self.config["EMBEDDING_MODEL"])
            logger.info(f"Loaded embedding model: {self.config['EMBEDDING_MODEL']}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _setup_vector_store(self):
        """Setup ChromaDB vector store"""
        try:
            # Create persistent client
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.config["VECTOR_STORE_PATH"]),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="alumni_network",
                metadata={"description": "Alumni profiles and network data"}
            )
            
            logger.info("ChromaDB vector store initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup vector store: {e}")
            raise
    
    async def add_document(self, document_text: str, metadata: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """Add document to vector store"""
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(document_text).tolist()
            
            # Generate ID if not provided
            if not doc_id:
                doc_id = str(uuid.uuid4())
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[document_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added document to vector store: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document to vector store: {e}")
            raise
    
    async def add_documents_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add multiple documents to vector store"""
        try:
            embeddings = []
            texts = []
            metadatas = []
            ids = []
            
            for doc in documents:
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})
                doc_id = doc.get("id", str(uuid.uuid4()))
                
                # Generate embedding
                embedding = self.embedding_model.encode(text).tolist()
                
                embeddings.append(embedding)
                texts.append(text)
                metadatas.append(metadata)
                ids.append(doc_id)
            
            # Add batch to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents batch to vector store: {e}")
            raise
    
    def search(self, query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search vector store for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare where clause for filtering
            where_clause = None
            if filters:
                where_clause = {}
                for key, value in filters.items():
                    if isinstance(value, str):
                        where_clause[key] = {"$eq": value}
                    elif isinstance(value, list):
                        where_clause[key] = {"$in": value}
                    else:
                        where_clause[key] = {"$eq": value}
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "relevance_rank": i + 1
                }
                formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search vector store: {e}")
            return []
    
    def search_with_context(self, query: str, context_filters: Dict[str, Any], 
                          limit: int = 10) -> Dict[str, Any]:
        """Search with additional context and generate insights"""
        try:
            # Search for relevant documents
            results = self.search(query, limit, context_filters)
            
            # Generate context-aware insights
            insights = self._generate_search_insights(query, results, context_filters)
            
            return {
                "query": query,
                "results": results,
                "insights": insights,
                "total_found": len(results),
                "context_filters": context_filters
            }
            
        except Exception as e:
            logger.error(f"Failed to search with context: {e}")
            return {
                "query": query,
                "results": [],
                "insights": {},
                "total_found": 0,
                "context_filters": context_filters
            }
    
    def get_similar_alumni(self, alumni_profile: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar alumni based on profile"""
        try:
            # Create search text from profile
            search_text = f"""
            Company: {alumni_profile.get('current_company', '')}
            Role: {alumni_profile.get('current_role', '')}
            Skills: {', '.join(alumni_profile.get('skills', []))}
            Industry: {alumni_profile.get('industry', '')}
            Experience: {alumni_profile.get('years_of_experience', 0)} years
            """
            
            # Search for similar profiles
            filters = {
                "type": "alumni_profile"
            }
            
            # Exclude the same alumni if searching for similar ones
            if alumni_profile.get("alumni_id"):
                filters["alumni_id"] = {"$ne": alumni_profile.get("alumni_id")}
            
            results = self.search(search_text, limit, filters)
            
            # Enhance results with similarity analysis
            for result in results:
                result["similarity_analysis"] = self._analyze_similarity(
                    alumni_profile, result.get("metadata", {})
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar alumni: {e}")
            return []
    
    def get_alumni_by_company(self, company_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get alumni from specific company"""
        try:
            filters = {
                "type": "alumni_profile",
                "company": {"$eq": company_name}
            }
            
            query = f"Alumni working at {company_name}"
            results = self.search(query, limit, filters)
            
            # Sort by experience level
            results.sort(key=lambda x: x.get("metadata", {}).get("years_of_experience", 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get alumni by company: {e}")
            return []
    
    def get_alumni_by_skills(self, skills: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Get alumni with specific skills"""
        try:
            query = f"Alumni with skills: {', '.join(skills)}"
            
            filters = {
                "type": "alumni_profile"
            }
            
            results = self.search(query, limit, filters)
            
            # Rank by skill match count
            for result in results:
                alumni_skills = result.get("metadata", {}).get("skills", [])
                if isinstance(alumni_skills, str):
                    alumni_skills = alumni_skills.split(", ")
                
                skill_matches = len(set(skills).intersection(set(alumni_skills)))
                result["skill_match_count"] = skill_matches
                result["skill_match_percentage"] = skill_matches / len(skills) if skills else 0
            
            # Sort by skill match count
            results.sort(key=lambda x: x.get("skill_match_count", 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get alumni by skills: {e}")
            return []
    
    def update_document(self, doc_id: str, updated_text: str, updated_metadata: Dict[str, Any]) -> bool:
        """Update existing document"""
        try:
            # Generate new embedding
            embedding = self.embedding_model.encode(updated_text).tolist()
            
            # Update in collection
            self.collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[updated_text],
                metadatas=[updated_metadata]
            )
            
            logger.info(f"Updated document in vector store: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector store"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document from vector store: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            
            # Get sample of documents to analyze
            sample_results = self.collection.get(limit=min(count, 100))
            
            # Analyze metadata
            metadata_analysis = self._analyze_metadata(sample_results.get("metadatas", []))
            
            return {
                "total_documents": count,
                "metadata_analysis": metadata_analysis,
                "collection_name": self.collection.name,
                "embedding_model": self.config["EMBEDDING_MODEL"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"total_documents": 0, "error": str(e)}
    
    def semantic_search_alumni(self, search_criteria: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search based on complex criteria"""
        try:
            # Build semantic query
            query_parts = []
            
            if search_criteria.get("target_role"):
                query_parts.append(f"Role: {search_criteria['target_role']}")
            
            if search_criteria.get("target_company"):
                query_parts.append(f"Company: {search_criteria['target_company']}")
            
            if search_criteria.get("required_skills"):
                query_parts.append(f"Skills: {', '.join(search_criteria['required_skills'])}")
            
            if search_criteria.get("industry"):
                query_parts.append(f"Industry: {search_criteria['industry']}")
            
            if search_criteria.get("experience_level"):
                query_parts.append(f"Experience level: {search_criteria['experience_level']}")
            
            semantic_query = " | ".join(query_parts)
            
            # Build filters
            filters = {"type": "alumni_profile"}
            
            if search_criteria.get("graduation_year_range"):
                start_year, end_year = search_criteria["graduation_year_range"]
                filters["graduation_year"] = {"$gte": start_year, "$lte": end_year}
            
            if search_criteria.get("min_experience"):
                filters["years_of_experience"] = {"$gte": search_criteria["min_experience"]}
            
            # Search
            results = self.search(semantic_query, limit * 2, filters)  # Get more for filtering
            
            # Post-process and rank results
            processed_results = self._post_process_semantic_results(results, search_criteria)
            
            return processed_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            return []
    
    def _generate_search_insights(self, query: str, results: List[Dict[str, Any]], 
                                context_filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from search results"""
        insights = {
            "query_analysis": self._analyze_query(query),
            "result_patterns": self._analyze_result_patterns(results),
            "recommendations": self._generate_recommendations(results, context_filters),
            "data_gaps": self._identify_data_gaps(results, context_filters)
        }
        
        return insights
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the search query"""
        query_lower = query.lower()
        
        analysis = {
            "query_type": "general",
            "contains_company": any(keyword in query_lower for keyword in ["company", "corp", "inc", "ltd"]),
            "contains_role": any(keyword in query_lower for keyword in ["engineer", "manager", "director", "analyst"]),
            "contains_skills": any(keyword in query_lower for keyword in ["python", "java", "react", "aws", "data"]),
            "specificity_score": len(query.split()) / 10.0  # Simple specificity measure
        }
        
        # Determine query type
        if analysis["contains_company"]:
            analysis["query_type"] = "company_focused"
        elif analysis["contains_role"]:
            analysis["query_type"] = "role_focused"
        elif analysis["contains_skills"]:
            analysis["query_type"] = "skill_focused"
        
        return analysis
    
    def _analyze_result_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in search results"""
        if not results:
            return {"pattern_summary": "No results to analyze"}
        
        # Extract metadata for analysis
        companies = []
        roles = []
        skills = []
        experience_levels = []
        
        for result in results:
            metadata = result.get("metadata", {})
            
            if metadata.get("company"):
                companies.append(metadata["company"])
            
            if metadata.get("role"):
                roles.append(metadata["role"])
            
            if metadata.get("skills"):
                if isinstance(metadata["skills"], list):
                    skills.extend(metadata["skills"])
                else:
                    skills.extend(metadata["skills"].split(", "))
            
            if metadata.get("years_of_experience"):
                experience_levels.append(metadata["years_of_experience"])
        
        # Count frequencies
        from collections import Counter
        
        patterns = {
            "top_companies": dict(Counter(companies).most_common(5)),
            "top_roles": dict(Counter(roles).most_common(5)),
            "top_skills": dict(Counter(skills).most_common(10)),
            "experience_distribution": {
                "junior": len([exp for exp in experience_levels if exp < 3]),
                "mid": len([exp for exp in experience_levels if 3 <= exp <= 7]),
                "senior": len([exp for exp in experience_levels if exp > 7])
            },
            "average_similarity": sum(r.get("similarity_score", 0) for r in results) / len(results)
        }
        
        return patterns
    
    def _generate_recommendations(self, results: List[Dict[str, Any]], 
                                context_filters: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on search results"""
        recommendations = []
        
        if not results:
            recommendations.append("Try broadening your search criteria")
            recommendations.append("Consider adding more alumni profiles to the database")
            return recommendations
        
        avg_similarity = sum(r.get("similarity_score", 0) for r in results) / len(results)
        
        if avg_similarity < 0.5:
            recommendations.append("Consider refining your search terms for better matches")
        
        if len(results) < 5:
            recommendations.append("Expand the search to include more graduation years or companies")
        
        # Check diversity
        companies = [r.get("metadata", {}).get("company") for r in results]
        unique_companies = len(set(filter(None, companies)))
        
        if unique_companies < len(results) / 2:
            recommendations.append("Search results show concentration in few companies - consider diversifying")
        
        if context_filters.get("type") == "alumni_profile":
            recommendations.append("Consider reaching out to top 3 matches for best referral potential")
        
        return recommendations
    
    def _identify_data_gaps(self, results: List[Dict[str, Any]], 
                          context_filters: Dict[str, Any]) -> List[str]:
        """Identify gaps in the data"""
        gaps = []
        
        if not results:
            gaps.append("No relevant alumni data found")
            return gaps
        
        # Check for missing metadata fields
        missing_fields = []
        required_fields = ["company", "role", "skills", "years_of_experience"]
        
        for field in required_fields:
            missing_count = sum(1 for r in results if not r.get("metadata", {}).get(field))
            if missing_count > len(results) * 0.3:  # More than 30% missing
                missing_fields.append(field)
        
        if missing_fields:
            gaps.append(f"Many profiles missing: {', '.join(missing_fields)}")
        
        # Check for recent data
        recent_profiles = sum(1 for r in results 
                            if r.get("metadata", {}).get("years_of_experience", 0) <= 2)
        
        if recent_profiles < len(results) * 0.2:  # Less than 20% recent graduates
            gaps.append("Limited recent graduate data available")
        
        return gaps
    
    def _analyze_similarity(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze similarity between two alumni profiles"""
        similarity_factors = {}
        
        # Company similarity
        if profile1.get("current_company") == profile2.get("company"):
            similarity_factors["same_company"] = True
        
        # Role similarity
        role1 = profile1.get("current_role", "").lower()
        role2 = profile2.get("role", "").lower()
        similarity_factors["role_similarity"] = self._calculate_text_similarity(role1, role2)
        
        # Skills similarity
        skills1 = set(profile1.get("skills", []))
        skills2_str = profile2.get("skills", "")
        skills2 = set(skills2_str.split(", ") if isinstance(skills2_str, str) else skills2_str)
        
        if skills1 and skills2:
            skill_overlap = len(skills1.intersection(skills2))
            skill_union = len(skills1.union(skills2))
            similarity_factors["skill_similarity"] = skill_overlap / skill_union if skill_union > 0 else 0
        else:
            similarity_factors["skill_similarity"] = 0
        
        # Experience similarity
        exp1 = profile1.get("years_of_experience", 0)
        exp2 = profile2.get("years_of_experience", 0)
        exp_diff = abs(exp1 - exp2)
        similarity_factors["experience_similarity"] = max(0, 1 - exp_diff / 10)  # Normalize to 0-1
        
        return similarity_factors
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _post_process_semantic_results(self, results: List[Dict[str, Any]], 
                                     search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Post-process semantic search results"""
        processed_results = []
        
        for result in results:
            metadata = result.get("metadata", {})
            
            # Calculate relevance score based on criteria
            relevance_score = 0.0
            criteria_count = 0
            
            # Role relevance
            if search_criteria.get("target_role"):
                role_sim = self._calculate_text_similarity(
                    search_criteria["target_role"],
                    metadata.get("role", "")
                )
                relevance_score += role_sim
                criteria_count += 1
            
            # Company relevance
            if search_criteria.get("target_company"):
                if metadata.get("company") == search_criteria["target_company"]:
                    relevance_score += 1.0
                criteria_count += 1
            
            # Skills relevance
            if search_criteria.get("required_skills"):
                alumni_skills_str = metadata.get("skills", "")
                alumni_skills = alumni_skills_str.split(", ") if isinstance(alumni_skills_str, str) else alumni_skills_str
                
                required_skills = search_criteria["required_skills"]
                skill_matches = len(set(required_skills).intersection(set(alumni_skills)))
                skill_relevance = skill_matches / len(required_skills) if required_skills else 0
                
                relevance_score += skill_relevance
                criteria_count += 1
            
            # Calculate final relevance score
            final_relevance = relevance_score / criteria_count if criteria_count > 0 else 0.5
            
            # Combine with similarity score
            combined_score = (result.get("similarity_score", 0) + final_relevance) / 2
            
            result["relevance_score"] = final_relevance
            result["combined_score"] = combined_score
            
            processed_results.append(result)
        
        # Sort by combined score
        processed_results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
        
        return processed_results
    
    def _analyze_metadata(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze metadata from a collection of documents"""
        if not metadata_list:
            return {"total_analyzed": 0}
        
        analysis = {
            "total_analyzed": len(metadata_list),
            "document_types": {},
            "companies": {},
            "roles": {},
            "graduation_years": {},
            "fields_coverage": {}
        }
        
        # Count field coverage
        all_fields = set()
        for metadata in metadata_list:
            all_fields.update(metadata.keys())
        
        for field in all_fields:
            coverage = sum(1 for metadata in metadata_list if metadata.get(field))
            analysis["fields_coverage"][field] = {
                "count": coverage,
                "percentage": (coverage / len(metadata_list)) * 100
            }
        
        # Count document types
        from collections import Counter
        
        types = [metadata.get("type", "unknown") for metadata in metadata_list]
        analysis["document_types"] = dict(Counter(types))
        
        companies = [metadata.get("company", "unknown") for metadata in metadata_list if metadata.get("company")]
        analysis["companies"] = dict(Counter(companies).most_common(10))
        
        roles = [metadata.get("role", "unknown") for metadata in metadata_list if metadata.get("role")]
        analysis["roles"] = dict(Counter(roles).most_common(10))
        
        return analysis
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            # Get all document IDs
            all_docs = self.collection.get()
            if all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
            
            logger.info("Cleared all documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    def reset_collection(self) -> bool:
        """Reset the entire collection"""
        try:
            # Delete and recreate collection
            self.chroma_client.delete_collection(name="alumni_network")
            self.collection = self.chroma_client.create_collection(
                name="alumni_network",
                metadata={"description": "Alumni profiles and network data"}
            )
            
            logger.info("Reset vector store collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False