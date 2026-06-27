BBVA RAG Assistant
Asistente conversacional basado en la arquitectura Retrieval-Augmented Generation (RAG). Este sistema permite a los usuarios consultar información institucional extraída del sitio web de BBVA mediante procesamiento de lenguaje natural.

Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado lo siguiente en tu máquina local:

Git: Para clonar el repositorio.

Docker y Docker Compose: Para la contenerización y orquestación de los servicios.

API Key de Groq: Necesaria para el consumo del modelo LLM. Puedes obtener una gratuita en Groq Console (https://console.groq.com/).

Instrucciones de Ejecución (Paso a Paso)

El sistema está completamente dockerizado para garantizar un despliegue sin fricciones. Sigue estos pasos para levantarlo desde cero:

Clonar el repositorio:
git clone https://github.com/CamiloesotoS98/bbva-rag-assistant.git
cd bbva-rag-assistant

Configurar las variables de entorno:
Crea un archivo llamado .env en la raíz del proyecto y agrega tu clave de Groq:
GROQ_API_KEY=gsk_tu_clave_generada_aqui

Levantar el sistema con Docker:
Ejecuta el siguiente comando para construir las imágenes y levantar los servicios:
docker compose up --build

Acceder a la aplicación:
Una vez que la consola indique que el contenedor está corriendo, abre tu navegador y dirígete a:
http://localhost:8501

Uso de la Interfaz Conversacional

Una vez en la aplicación, la interfaz es intuitiva:

Panel Lateral (Sidebar): Permite iniciar una "Nueva Conversación" para limpiar el contexto y gestionar sesiones previas. Al hacer clic en una sesión del historial, el sistema recupera automáticamente el contexto guardado en la base de datos SQLite.

Área de Chat: Escribe tus consultas financieras en la caja de texto inferior. El sistema recuperará información relevante de la base documental y responderá basándose en el contexto del sitio web de BBVA.

Patrones de Diseño Usados

Para asegurar un código escalable y mantenible:

Singleton (src/patterns/singleton.py): Aplicado en ChatDatabase. Garantiza que exista una única instancia de conexión a la base de datos, evitando conflictos de concurrencia al gestionar el historial en SQLite.

Factory Method (src/patterns/factory.py): Aplicado en LLMFactory. Centraliza la instanciación de modelos de lenguaje, permitiendo cambiar de proveedor (ej. Groq a OpenAI) sin modificar la lógica central del RAG.

Strategy (src/patterns/strategy.py): Aplicado en el módulo de Web Scraping. Permite intercambiar algoritmos de extracción (ej. BeautifulSoup vs Playwright) de forma flexible para adaptarse a diferentes estructuras de sitios web.

Stack Tecnológico y Justificación

Python 3.12: Lenguaje base por su ecosistema robusto en IA.

LangChain: Framework para la orquestación de la cadena RAG.

Groq (Llama-3.1-8b): Seleccionado por su velocidad de inferencia extrema y tier gratuito.

ChromaDB: Base de datos vectorial self-hosted ideal para almacenamiento local eficiente.

SQLite: Motor de base de datos relacional ligero para persistir el historial de sesiones de manera inmediata.

Streamlit: Permite el despliegue rápido de una interfaz gráfica reactiva exclusivamente con Python.

Limitaciones y Decisiones de Diseño

Ingesta por lotes: Por motivos de optimización, el scraping se realiza como un proceso de ingesta inicial y no en tiempo real.

Ventana de contexto: Para mantener la latencia baja, se recuperan los últimos N mensajes (configurables), limitando el historial total en la llamada al LLM.

Hardware: El despliegue requiere virtualización habilitada para Docker.

Futuras Mejoras

Implementación de Reranker: Integrar un modelo de reordenamiento semántico para incrementar la precisión de la recuperación.

Pipeline ETL Automatizado: Programar actualizaciones periódicas del scraper para mantener el conocimiento vectorial actualizado.