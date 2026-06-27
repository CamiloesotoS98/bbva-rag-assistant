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

from database import ChatDatabase
from patterns.factory import LLMFactory

load_dotenv()

# 1. CONFIGURACIÓN VISUAL DE LA PÁGINA (Debe ser la primera instrucción)
st.set_page_config(page_title="BBVA Assistant", page_icon="🏦", layout="wide")

# 2. INYECCIÓN DE CSS AVANZADO
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Mejorar la apariencia de la caja de chat */
        .stChatInputContainer {
            padding-bottom: 20px;
        }
        
        /* Darle un fondo blanco y sombra sutil al área de mensajes */
        .stChatMessage {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. GESTIÓN DE SESIÓN Y BASE DE DATOS
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

db = ChatDatabase()

# 4. CARGA DEL PIPELINE RAG
@st.cache_resource
def load_rag_pipeline():
    base_dir = Path(__file__).resolve().parent.parent
    chroma_dir = base_dir / "data" / "chroma_db"
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(persist_directory=str(chroma_dir), embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    llm = LLMFactory.create_llm(provider="groq")
    
    system_prompt = (
        "Eres un asesor financiero virtual experto, profesional y amable de BBVA Colombia. "
        "Usa EXCLUSIVAMENTE el siguiente contexto recuperado de la web para responder. "
        "Si no sabes la respuesta o no está en el contexto, indica amablemente que no dispones de esa información. "
        "Contexto:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

try:
    rag_chain = load_rag_pipeline()
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# 5. DISEÑO DE LA INTERFAZ: BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.markdown("## 🏦 BBVA RAG Assistant")
    st.markdown("---")
    st.info(f"**ID de Sesión:**\n`{st.session_state.session_id[:8]}...`")
    
    st.markdown("### 💡 Sugerencias:")
    st.markdown("- *¿Qué tarjetas de crédito tienen?*")
    st.markdown("- *Explícame los beneficios de la tarjeta Aqua.*")
    
    st.markdown("---")
    if st.button("🔄 Nueva Conversación", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# 6. DISEÑO DE LA INTERFAZ: ÁREA PRINCIPAL
st.title("Asistente Virtual Institucional")
st.markdown("Hola. Soy tu asistente financiero impulsado por Inteligencia Artificial. ¿En qué te puedo ayudar hoy?")

# Recuperar y mostrar historial con avatares personalizados
raw_history = db.get_recent_history(st.session_state.session_id, limit=6)
langchain_history = []

for msg in raw_history:
    # Asignamos "👤" al usuario y "🏦" al asistente
    avatar_icon = "👤" if msg["role"] == "user" else "🏦"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])
        
    if msg["role"] == "user":
        langchain_history.append(HumanMessage(content=msg["content"]))
    else:
        langchain_history.append(AIMessage(content=msg["content"]))

# 7. CAPTURA DE NUEVO MENSAJE
if user_input := st.chat_input("Escribe tu consulta aquí..."):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    db.save_message(st.session_state.session_id, "user", user_input)
    
    with st.chat_message("assistant", avatar="🏦"):
        with st.spinner("Consultando la base de conocimiento..."):
            response = rag_chain.invoke({
                "input": user_input,
                "chat_history": langchain_history
            })
            answer = response["answer"]
            st.markdown(answer)
            
    db.save_message(st.session_state.session_id, "assistant", answer)