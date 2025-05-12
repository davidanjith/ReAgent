from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import Dict, List
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class ChatEngine:
    def __init__(self):
        # Initialize Ollama with secure settings
        self.llm = Ollama(
            model="llama2:latest",
            temperature=0.7,
            stop=["Human:", "Assistant:"],  # Prevent prompt injection
            timeout=30  # Add timeout to prevent hanging
        )
        
        # Create a secure prompt template for paper-specific chat
        self.paper_chat_template = """You are an AI research assistant helping to analyze and discuss academic papers.
        You have access to the following paper information:
        
        Title: {title}
        Authors: {authors}
        Abstract: {abstract}
        
        Current conversation:
        {history}
        
        Human: {input}
        Assistant:"""
        
        self.paper_chat_prompt = PromptTemplate(
            input_variables=["title", "authors", "abstract", "history", "input"],
            template=self.paper_chat_template
        )
        
        # Initialize memory with default values for paper details
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
            input_key="input",
            output_key="output"
        )
        
        # Initialize conversation chain with default values
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        
        # Initialize knowledge graph
        self.knowledge_graph = {
            "nodes": [],
            "edges": []
        }

    async def chat(self, message: str, context: str = "", paper_id: str = None) -> Dict:
        """
        Process a chat message and return a response
        """
        try:
            # Sanitize input
            message = self._sanitize_input(message)
            context = self._sanitize_input(context)
            
            # Default paper details
            paper_details = {
                "title": "",
                "authors": "",
                "abstract": ""
            }
            
            # If paper_id is provided, extract paper details from context
            if paper_id:
                for line in context.split('\n'):
                    if line.startswith('Paper:'):
                        paper_details['title'] = line.replace('Paper:', '').strip()
                    elif line.startswith('Abstract:'):
                        paper_details['abstract'] = line.replace('Abstract:', '').strip()
            
            # Format the prompt with paper details
            prompt = self.paper_chat_prompt.format(
                title=paper_details['title'],
                authors=paper_details['authors'],
                abstract=paper_details['abstract'],
                history=self.memory.buffer,
                input=message
            )
            
            # Get response from LLM using asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.llm.predict, prompt)
            
            # Update memory
            self.memory.save_context({"input": message}, {"output": response})
            
            # Extract key concepts and relationships
            self._update_knowledge_graph(message, response)
            
            return {
                "response": response,
                "knowledge_graph": self.knowledge_graph
            }
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

    def _sanitize_input(self, text: str) -> str:
        """
        Sanitize input to prevent injection attacks
        """
        # Remove any potential command injection characters
        sanitized = text.replace(";", "").replace("|", "").replace("&", "")
        # Remove any potential path traversal attempts
        sanitized = sanitized.replace("../", "").replace("..\\", "")
        return sanitized

    def _update_knowledge_graph(self, user_input: str, response: str):
        """
        Update the knowledge graph with new information
        """
        # Extract key concepts from the conversation
        concepts = self._extract_concepts(user_input, response)
        
        # Add new nodes and edges to the graph
        for concept in concepts:
            if concept not in self.knowledge_graph["nodes"]:
                self.knowledge_graph["nodes"].append(concept)
            
            # Add relationships between concepts
            for other_concept in concepts:
                if concept != other_concept:
                    edge = {
                        "source": concept,
                        "target": other_concept,
                        "type": "related"
                    }
                    if edge not in self.knowledge_graph["edges"]:
                        self.knowledge_graph["edges"].append(edge)

    def _extract_concepts(self, user_input: str, response: str) -> List[str]:
        """
        Extract key concepts from the conversation
        """
        # Use the LLM to extract key concepts with a secure prompt
        prompt = f"""
        Extract the key concepts from this conversation. Return only a JSON array of strings.
        Do not include any code execution or system commands.
        
        User: {user_input}
        Assistant: {response}
        """
        
        try:
            result = self.llm(prompt)
            concepts = json.loads(result)
            # Validate that concepts is a list of strings
            if isinstance(concepts, list) and all(isinstance(c, str) for c in concepts):
                return concepts
        except:
            pass
        
        # Fallback to simple word extraction if JSON parsing fails
        words = set(user_input.split() + response.split())
        return list(words)

    def get_knowledge_graph(self) -> Dict:
        """
        Get the current state of the knowledge graph
        """
        # Ensure nodes are unique and properly formatted
        nodes = list(set(self.knowledge_graph["nodes"]))
        
        # Create edges with proper source and target indices
        edges = []
        for edge in self.knowledge_graph["edges"]:
            try:
                source_idx = nodes.index(edge["source"])
                target_idx = nodes.index(edge["target"])
                edges.append({
                    "source": source_idx,
                    "target": target_idx,
                    "type": edge.get("type", "related")
                })
            except ValueError:
                continue  # Skip edges with nodes that don't exist
        
        return {
            "nodes": nodes,
            "edges": edges
        } 