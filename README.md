#  BBVA RAG Assistant

Asistente conversacional basado en la arquitectura **Retrieval-Augmented Generation (RAG)**. Este sistema permite a los usuarios consultar información institucional extraída del sitio web de BBVA mediante procesamiento de lenguaje natural.

---

##  Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado lo siguiente en tu máquina local:

* **Git:** Para clonar el repositorio.
* **Docker y Docker Compose:** Para la contenerización y orquestación de los servicios (asegúrate de que Docker Desktop o el demonio de Docker esté en ejecución).
* **API Key de Groq:** Necesaria para el consumo del modelo LLM. Puedes obtener una gratuita en [Groq Console](https://console.groq.com/).

---

##  Instrucciones de Ejecución (Paso a Paso)

El sistema está completamente dockerizado para garantizar un despliegue sin fricciones. Sigue estos pasos para levantarlo desde cero:

1. **Clonar el repositorio:**
```bash
git clone [https://github.com/TU_USUARIO/bbva-rag-assistant.git](https://github.com/CamiloesotoS98/bbva-rag-assistant.git)
cd bbva-rag-assistant