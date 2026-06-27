import os
import json
from pathlib import Path
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentIndexer:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.clean_dir = self.base_dir / "data" / "clean"
        self.chroma_dir = self.base_dir / "data" / "chroma_db"
        logging.info("Cargando modelo de embeddings local...")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            persist_directory=str(self.chroma_dir),
            embedding_function=self.embeddings
        )

    def load_json_documents(self) -> list[Document]:
        """Lee todos los archivos JSON limpios y los convierte en objetos Document."""
        documents = []
        if not self.clean_dir.exists():
            logging.error(f"El directorio {self.clean_dir} no existe. Ejecuta el scraper primero.")
            return documents

        for file_path in self.clean_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = data.get("content", "")
                    url = data.get("url", file_path.name)
                    
                    if content:
                        doc = Document(
                            page_content=content,
                            metadata={"source": url}
                        )
                        documents.append(doc)
                        logging.info(f"Documento cargado con éxito: {file_path.name}")
            except Exception as e:
                logging.error(f"Error al leer {file_path.name}: {e}")
                
        return documents

    def index_documents(self):
        """Carga, divide e indexa los documentos en ChromaDB."""
        docs = self.load_json_documents()
        
        if not docs:
            logging.warning("❌ No se encontraron documentos para indexar.")
            return

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        logging.info("Dividiendo documentos en chunks (fragmentos)...")
        splits = text_splitter.split_documents(docs)
        logging.info(f"Se generaron {len(splits)} fragmentos para analizar.")
        
        logging.info("Vectorizando y guardando en ChromaDB...")
        self.vector_store.add_documents(splits)
        
        logging.info("✅ ¡Indexación completada! Los vectores están en data/chroma_db.")

if __name__ == "__main__":
    indexer = DocumentIndexer()
    indexer.index_documents()