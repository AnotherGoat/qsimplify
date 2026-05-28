# QSimplify Pricing Engine

Este módulo es el núcleo financiero de QSimplify. Su objetivo es obtener precios en tiempo real del hardware cuántico (AWS e IBM) y cruzarlos con un estimador de tiempo basado en grafos para predecir el costo total de ejecución de un circuito.

## Estado Actual (Características Implementadas)

El motor cuenta con dos pilares principales totalmente integrados:

### 1. Adquisición Dinámica de Datos (`scraperv2.py` y `viewer.py`)

- **AWS Braket:** Se conecta a la *AWS Price List API* para obtener precios por tarea y por shot de las QPUs.
- **IBM Quantum:** Realiza web scraping y consulta la API del Catálogo Global para extraer tarifas por segundo.
- **Caché (`pricing_cache.json`):** Almacenamiento local inteligente con 24 horas de expiración para evitar baneos y bloqueos de red.
- **Viewer:** Visualizador de terminal usando la librería `rich`.

### 2. Estimador de Tiempos y Costos (`time_estimator.py` y `estimator_api.py`)

- **Algoritmo de Ruta Crítica:** Simula las barreras de ejecución del hardware cuántico. Rastreando el "reloj interno" de cada qubit, calcula el tiempo máximo (ruta crítica) considerando operaciones en paralelo y tiempos de espera en compuertas multi-qubit.
- **Costos Heurísticos:** Usa pesos abstractos (`BackendProfile`) para flexibilizar la compatibilidad con diferentes arquitecturas.
- **API REST (FastAPI):** Punto de acceso principal (`/estimate`). Recibe el circuito y:
  1. Calcula la puntuación heurística de tiempo.
  2. Convierte el tiempo abstracto a nanosegundos reales (mediante `base_time_ns`).
  3. Llama al scraper de precios.
  4. Retorna el costo monetario total en la nube simulando la facturación real (ej. cobro por segundo en IBM, cobro por tarea en AWS).

## Fórmulas de Estimación

Para poder calcular la eficiencia de un circuito (y permitir que el simplificador tome decisiones correctas), el motor utiliza las siguientes fórmulas matemáticas:

### 1. Tiempo de Ejecución (Ruta Crítica)

El algoritmo trata al circuito cuántico como un Grafo Acíclico Dirigido (DAG). El tiempo total no es la suma de todas las compuertas, sino el tiempo del camino más largo (ruta crítica), ya que las operaciones independientes se ejecutan en paralelo.

Para cada compuerta $g$ que opera sobre un conjunto de qubits $Q$, el tiempo de finalización se calcula como:

$$
t_{end}(g) = \max_{q \in Q}(t_{ready}(q)) + Costo(g)
$$

El tiempo total de una sola repetición es el máximo tiempo de finalización entre todos los qubits, sumado al tiempo obligatorio de enfriamiento (`repetition_delay_cost`). Finalmente se multiplica por el total de mediciones (`shots`):

$$
Tiempo_{Total} = Shots \times (t_{max} + Retraso)
$$

### 2. Cálculo de Costos Reales

Una vez obtenido el tiempo heurístico del DAG, se cruza con los precios extraídos de la web:

- **AWS Braket (Cobro por Tarea):** AWS no cobra por tiempo, sino una tarifa fija por subir el circuito, más una tarifa diminuta por cada "shot".

  $$
  Costo_{AWS} = Precio_{Tarea} + (Shots \times Precio_{Shot})
  $$
- **IBM Quantum (Cobro por Tiempo):** IBM cobra por la en fracción de segundo que el procesador estuvo trabajando para ti. Por ello, transformamos nuestro tiempo abstracto a nanosegundos usando la escala del procesador, y luego a segundos reales:

  $$
  Segundos = \frac{Tiempo_{Total} \times base\_time\_ns}{1,000,000,000}
  $$

  $$
  Costo_{IBM} = Segundos \times Tarifa_{Segundo}
  $$

## Cómo Ejecutar la API

Puedes levantar el servidor localmente ejecutando:

```bash
.venv\Scripts\python.exe pricing_engine\estimator_api.py
```

O simplemente haciendo click en "Run" desde el IDE en el archivo `estimator_api.py`. Luego, ingresa a `http://127.0.0.1:5002/docs` para acceder a la interfaz interactiva de Swagger UI y probar las estimaciones.

## Ejemplo de Uso (Endpoint `/estimate`)

Al enviar una petición `POST` al endpoint `/estimate`, se debe proporcionar una estructura JSON que defina las compuertas del circuito, la cantidad de `shots` (repeticiones) y el perfil de hardware (`backend_profile`) que dicta los pesos heurísticos.

### Petición (Request)

```json
{
  "gates": [
    { "name": "h", "qubit": 0 },
    { "name": "cx", "control_qubit": 0, "target_qubit": 1 }
  ],
  "shots": 1000,
  "backend_profile": {
    "phase_cost": 0,
    "single_qubit_cost": 1,
    "sqrt_cost": 2,
    "two_qubit_cost": 15,
    "three_qubit_cost": 80,
    "swap_cost": 45,
    "measure_cost": 200,
    "reset_cost": 200,
    "repetition_delay_cost": 100,
    "base_time_ns": 30.0
  }
}
```

### Respuesta (Response)

La API devolverá un JSON que incluye el tiempo heurístico del circuito y un listado con los costos calculados en dólares reales para las distintas máquinas de los proveedores en la nube.

```json
{
  "execution_time": 316000.0,
  "costs": [
    {
      "provider": "IBM Quantum",
      "status": "success",
      "estimates": [
        {
          "provider": "IBM",
          "plan_name": "Pay-As-You-Go Plan",
          "price_label": "$96 USD / minute",
          "cost_usd": 0.015168
        }
      ]
    },
    {
      "provider": "AWS Braket",
      "status": "success",
      "estimates": [
        {
          "provider": "IonQ",
          "plan_name": "Harmony",
          "price_label": "Per task + per shot",
          "cost_usd": 10.3
        }
      ]
    }
  ]
}
```
