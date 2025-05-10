from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import Dict, List
import json

class ChatEngine:
    def __init__(self):
        # Initialize Ollama with secure settings
        self.llm = Ollama(
            model="llama2:latest",
            temperature=0.7,
            stop=["Human:", "Assistant:"],  # Prevent prompt injection
            timeout=30  # Add timeout to prevent hanging
        )
        
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
        
        # Initialize knowledge graph
        self.knowledge_graph = {
            "nodes": [],
            "edges": []
        }

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