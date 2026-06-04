# Verificación y Control de Calidad (QA)

> [← Volver al índice](index.md)

---

Este documento detalla la estrategia de control de calidad (QA), el entorno de pruebas unitarias offline y las mejoras de robustez introducidas en el sistema para garantizar ejecuciones confiables en producción.

---

## 🛡️ Auditoría de Robustez y Mejoras Introducidas

Durante la auditoría QA, se detectaron y corrigieron múltiples bugs de consistencia interna y estabilidad. A continuación, se detallan las mejoras clave:

| Módulo | Tipo de Ajuste | Descripción del Cambio | Beneficio |
|---|---|---|---|
| **`app/llm.py`** | Carga de Entorno | Se movió `load_dotenv()` al nivel de importación de módulo. | Las API keys están disponibles independientemente del punto de entrada (servidor MCP, CLI o API). |
| **`app/publisher.py`** | Validación de Entradas | Parámetro `status` y URLs ahora se validan *antes* de iniciar llamadas HTTP. | Evita llamadas de red inválidas y fallos silenciosos, levantando `ValueError` inmediatos. |
| **`app/seo.py`** | Validación de Entradas | `audit_content` ahora requiere contenido y keyword principal no vacíos. | Robustez de la capa de lógica, previniendo análisis con datos corruptos o vacíos. |
| **`app/models.py`** | Generación Dinámica | El validador de `slug` en `ContentMetadata` ahora autogenera el slug si viene vacío. | Simplifica la construcción de metadatos de post por parte de agentes o scripts externos. |
| **`app/core.py`** | Fachada e Integración | Persistencia automática en base de datos JSON local al generar artículos. | Sincronización perfecta del historial sin requerir llamadas manuales de guardado. |

---

## 🧪 Estrategia de Pruebas Unitarias Offline

Para permitir un desarrollo ágil y la ejecución en entornos de Integración Continua (CI/CD) sin dependencias de red ni consumo de tokens, se implementó un **framework de testing 100% offline**.

### 1. Mocking Dinámico de LLM (`call_llm`)
Se utiliza `unittest.mock.patch` para interceptar todas las importaciones de `call_llm` en los módulos de generación, SEO e investigación. 

El mock analiza semánticamente el prompt recibido y retorna respuestas simuladas estructuradas según el formato esperado:
- **Respuestas JSON** para análisis competitivos.
- **Listas numeradas** para hallazgos y tendencias.
- **Meta descripciones dinámicas** conteniendo el tema exacto que el test está verificando.

### 2. Prevención de Interferencia de Directorios Temporales
Dado que el gestor de persistencia (`StorageManager`) y la fachada utilizan el patrón **Singleton**, existía el riesgo de que la ruta de almacenamiento de un test anterior interfiriera con los test subsiguientes (especialmente al usar directorios temporales de corta vida).

Se añadió un mecanismo de reset de singletons en el método `setUp` de los tests:
```python
def setUp(self):
    # Forzar el reset de los singletons antes de cada caso de prueba
    import app.storage
    import app.core
    app.storage._storage_manager = None
    app.core._content_generator = None
    
    self.temp_dir = tempfile.TemporaryDirectory()
    self.generator = ContentGenerator(Path(self.temp_dir.name))
```
Esto garantiza aislamiento total entre cada caso de prueba y ejecuciones consistentes.

---

## ⚙️ Ejecución de la Suite de Pruebas

Para ejecutar las pruebas del sistema, navega al directorio raíz del proyecto y usa el módulo `unittest` de Python:

```bash
# Ejecutar todas las pruebas unitarias
python -m unittest tests/test_core.py
```

### Resultados Esperados
Deberías obtener una salida limpia con los 25 tests completados exitosamente:

```
Ran 25 tests in 0.139s

OK
```

---

## 🔄 Capa de Retrocompatibilidad de la Fachada

Para proteger las integraciones existentes de clientes MCP y scripts heredados, la fachada `ContentGenerator` en [core.py](file:///c:/Users/P0zcl/Desktop/wp_mcp_content_ai/app/core.py) expone delegados privados que dirigen las llamadas a los nuevos motores especializados:

```python
# Métodos delegados para preservar la compatibilidad con código cliente antiguo
self.generator._generate_slug(topic)           # -> Delega a ContentGeneratorEngine
self.generator._generate_meta_description(...)  # -> Delega a ContentGeneratorEngine
self.generator._calculate_seo_score(...)       # -> Delega a SEOAuditor
self.generator._generate_seo_recommendations()  # -> Delega a SEOAuditor
self.generator._optimize_content(...)          # -> Delega a SEOAuditor
```
