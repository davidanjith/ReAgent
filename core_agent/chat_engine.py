from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import Dict, List
import json
import logging

# Get logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ChatEngine:
    def __init__(self):
        logger.info("Initializing ChatEngine...")
        # Initialize Ollama with GPU acceleration
        self.llm = Ollama(
            model="llama3:latest",
            temperature=0.7,
            stop=["Human:", "Assistant:"],  # Prevent prompt injection
            timeout=30,  # Add timeout to prevent hanging
            num_gpu=1,  # Enable GPU acceleration
            num_thread=4  # Adjust based on your CPU cores
        )
        logger.info("Ollama LLM initialized successfully")
        
        # Create a secure prompt template
        template = """The following is a friendly conversation between a human and an AI. 
        The AI is helpful, creative, clever, and very friendly.
        
        Current conversation:
        {history}
        Human: {input}
        Assistant:"""
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
        
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history"
        )
        
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )
        logger.info("Conversation chain initialized successfully")
        
        # Initialize knowledge graph
        self.knowledge_graph = {
            "nodes": [],
            "edges": []
        }
        logger.info("ChatEngine initialization completed")

    async def chat(self, message: str, context: str = "") -> Dict:
        """
        Process a chat message and return a response
        """
        # Sanitize input
        message = self._sanitize_input(message)
        context = self._sanitize_input(context)
        
        prompt = f"Context: {context}\n\nUser: {message}"
        response = self.conversation.predict(input=prompt)
        
        # Extract key concepts and relationships
        self._update_knowledge_graph(message, response)
        
        return {
            "response": response,
            "knowledge_graph": self.knowledge_graph
        }

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
            result = self.llm.invoke(prompt)
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
        Return the current state of the knowledge graph
        """
        return self.knowledge_graph 