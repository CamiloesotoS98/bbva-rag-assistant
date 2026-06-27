# src/patterns/factory.py
import os
from langchain_groq import ChatGroq

class LLMFactory:
    """
    Patrón Creacional: Factory Method.
    Centraliza la creación de los modelos de lenguaje (LLMs).
    Permite cambiar de proveedor (Groq, OpenAI, Local) fácilmente en un solo lugar.
    """
    @staticmethod
    def create_llm(provider: str = "groq", temperature: float = 0.0):
        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("La variable de entorno GROQ_API_KEY no está configurada.")
            
            # ACTUALIZACIÓN: Usamos el modelo Llama 3.1 más reciente soportado por Groq
            return ChatGroq(
                temperature=temperature, 
                model_name="llama-3.1-8b-instant", 
                groq_api_key=api_key
            )
        else:
            raise NotImplementedError(f"El proveedor {provider} no está soportado aún.")