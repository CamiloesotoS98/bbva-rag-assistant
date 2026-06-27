# src/app.py
import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Importamos nuestros propios módulos
from database import ChatDatabase
from patterns.factory import LLMFactory

# Cargar variables de entorno (el archivo .env)
load_dotenv()

# Configuración visual de la página
st.set_page_config(page_title="Asistente RAG", page_icon="🏦", layout="centered")
st.title("🏦 Asistente Virtual Financiero")

# Inicializar un ID de sesión único para cada usuario que abre la web
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Conectar a nuestra base de datos Singleton
db = ChatDatabase()

@st.cache_resource
def load_rag_pipeline():
    """Carga y cachea la cadena RAG para que no se recargue en cada mensaje."""
    base_dir = Path(__file__).resolve().parent.parent
    chroma_dir = base_dir / "data" / "chroma_db"
    
    # 1. Conectar a ChromaDB local
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(persist_directory=str(chroma_dir), embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # 2. Instanciar LLM usando nuestro Patrón Factory
    llm = LLMFactory.create_llm(provider="groq")
    
    # 3. Crear el Prompt del Asistente
    system_prompt = (
        "Eres un asistente virtual amable y experto de un banco en Colombia. "
        "Usa el siguiente contexto recuperado de la web para responder la pregunta del usuario. "
        "Si la respuesta no está en el contexto, di honestamente que no tienes esa información. "
        "Contexto:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

# Intentar cargar el RAG
try:
    rag_chain = load_rag_pipeline()
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# ==========================================
# Lógica de Interfaz y Memoria
# ==========================================

# 1. Recuperar historial (N = 6 mensajes) desde SQLite
raw_history = db.get_recent_history(st.session_state.session_id, limit=6)
langchain_history = []

# 2. Mostrar los mensajes antiguos en la pantalla
for msg in raw_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
    # Formatear el historial para que LangChain lo entienda
    if msg["role"] == "user":
        langchain_history.append(HumanMessage(content=msg["content"]))
    else:
        langchain_history.append(AIMessage(content=msg["content"]))

# 3. Capturar la nueva pregunta del usuario
if user_input := st.chat_input("Pregunta sobre tarjetas de crédito, cuentas, etc..."):
    
    # Imprimir en pantalla y guardar en BD
    with st.chat_message("user"):
        st.markdown(user_input)
    db.save_message(st.session_state.session_id, "user", user_input)
    
    # Consultar al modelo con la pregunta y el historial
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la base de datos documental..."):
            response = rag_chain.invoke({
                "input": user_input,
                "chat_history": langchain_history
            })
            answer = response["answer"]
            st.markdown(answer)
            
    # Guardar respuesta del bot en BD
    db.save_message(st.session_state.session_id, "assistant", answer)