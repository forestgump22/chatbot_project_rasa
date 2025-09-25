# Arquitectura y Funcionamiento de RASA

RASA es una plataforma de asistentes conversacionales que se diferencia de los chatbots basados exclusivamente en modelos de lenguaje de gran escala (LLMs). Su principal característica es que puede ejecutarse completamente en local o en servidores propios, sin depender de conexión a internet para sus funciones principales. La integración con servicios externos, como Gemini, es opcional y funciona como un complemento, no como el núcleo del sistema.

---

## Componentes Principales: Los Dos "Cerebros" de RASA

RASA combina dos módulos fundamentales que trabajan de manera coordinada. Ambos emplean modelos de *Machine Learning* que se entrenan con datos específicos del usuario, lo cual otorga un control completo sobre su comportamiento.

### 1. RASA NLU (Natural Language Understanding) – El Traductor

- **Función:** Interpretar el lenguaje natural de los usuarios y convertirlo en información estructurada.  
- **Salidas principales:**
  1. **Intents:** Identifican la intención del usuario (ejemplo: `verificar_stock`).  
  2. **Entities:** Extraen los elementos clave de la frase (ejemplo: `producto: "laptop gamer Alienware"`).  
- **Tecnología empleada:**  
  - Basado en modelos especializados y ligeros definidos en el `pipeline` de `config.yml`.  
  - El clasificador principal es el **DIETClassifier (Dual Intent and Entity Transformer)**, que utiliza arquitectura *Transformer*.  
  - Los modelos son pequeños, rápidos y se ajustan únicamente a los datos provistos en `nlu.yml`.  

### 2. RASA Core (Dialogue Management) – El Estratega

- **Función:** Gestionar el flujo de la conversación y decidir la acción a ejecutar en cada momento.  
- **Acciones posibles:**  
  - Emitir una respuesta predefinida (`utter_...` en `domain.yml`).  
  - Ejecutar código personalizado (`action_...` en `actions.py`).  
  - Esperar la próxima entrada del usuario.  
- **Tecnología empleada:**  
  - Se apoya en políticas configuradas en `config.yml`.  
  - **MemoizationPolicy:** Ejecuta acciones cuando encuentra coincidencias exactas con ejemplos en `stories.yml`.  
  - **RulePolicy:** Aplica reglas estrictas definidas manualmente.  
  - **TEDPolicy (Transformer Embedding Dialogue Policy):** Modelo basado en *Transformer* que analiza secuencias completas de conversaciones para predecir la acción más adecuada.  

---

## Flujo de Trabajo Interno de RASA

1. El usuario envía un mensaje: *"Quiero agendar una cita con un dentista"*.  
2. **RASA NLU** procesa el texto mediante el `pipeline` y devuelve:  
   - `intent: agendar_cita`  
   - `entity: especialidad: "dentista"`  
3. El **Tracker** actualiza el estado de la conversación (intenciones previas, slots, etc.).  
4. **RASA Core** consulta las políticas configuradas:  
   - La `MemoizationPolicy` busca coincidencias en `stories.yml`.  
   - La `TEDPolicy` evalúa la secuencia de diálogo y predice la acción más apropiada.  
   - Se determina ejecutar `action_agendar_cita`.  
5. El **Servidor de Acciones** ejecuta la lógica definida en `actions.py`.  
6. Se genera la respuesta y se envía de vuelta al usuario.  

---

## Funcionalidades y Casos de Uso

RASA está diseñado para asistentes conversacionales orientados a objetivos (*Goal-Oriented Conversational Assistants*), siendo especialmente eficaz en entornos donde se requieren interacciones estructuradas y confiables.

### Fortalezas Principales

1. **Automatización de procesos de negocio:**  
   - Reservas y citas (viajes, restaurantes, salud).  
   - Soporte al cliente de primer nivel (preguntas frecuentes, apertura de tickets).  
   - Transacciones seguras (consultas de saldo, transferencias, compras).  

2. **Control y fiabilidad:**  
   - El entrenamiento con datos propios hace que el comportamiento sea predecible.  
   - Reduce el riesgo de respuestas erróneas o inventadas, comunes en LLMs.  

3. **Privacidad y seguridad:**  
   - Puede ejecutarse íntegramente en servidores internos (*on-premise*).  
   - Recomendado para sectores sensibles como banca, salud y gobierno.  

4. **Integración con sistemas externos:**  
   - El archivo `actions.py` permite conectar el asistente con bases de datos, APIs, CRMs y otros sistemas corporativos.  

5. **Arquitectura híbrida:**  
   - RASA puede gestionar la estructura del diálogo y, en situaciones que requieran flexibilidad o conocimiento general, apoyarse en un LLM como Gemini.  
   - De esta manera, se combina el control de RASA con la versatilidad de un modelo de lenguaje.  

---

## Conclusión

RASA constituye la base robusta y confiable de un chatbot orientado a tareas específicas. Su diseño garantiza control, precisión y privacidad, mientras que la integración con LLMs ofrece capacidades adicionales cuando son necesarias. De este modo, RASA actúa como el **esqueleto estructurado** del asistente conversacional, y los LLMs como **herramientas complementarias** que enriquecen su funcionamiento.
