# QSimplify Pricing Engine 💸

Este módulo es el núcleo financiero de QSimplify. Su objetivo actual es obtener, almacenar en caché y visualizar de forma dinámica los precios en tiempo real del hardware cuántico de los principales proveedores de la nube (AWS e IBM).

## 🚀 Estado Actual (Qué tenemos implementado)

Hasta el momento, el motor cuenta con una infraestructura robusta para la obtención de datos, compuesta por los siguientes elementos:

1. **Adquisición Dinámica de Datos (`scraperv2.py`)**
   - **AWS Braket:** Se conecta directamente a la *AWS Price List API* oficial para obtener los precios bajo demanda (cobro por tarea + cobro por shot) de todas sus QPU (IonQ, Rigetti, IQM, etc.).
   - **IBM Quantum:** Utiliza un enfoque híbrido. Realiza un *Web Scraping* de la página pública para listar todos los planes, y como respaldo, consulta la *API del Catálogo Global de IBM* para extraer el precio exacto por segundo de su plan *Pay-As-You-Go*.

2. **Sistema de Caché Inteligente**
   - Para evitar bloqueos, baneos de IP o la aparición de CAPTCHAs por realizar demasiadas peticiones, el scraper guarda los resultados en el archivo local `pricing_cache.json`.
   - La caché tiene un tiempo de expiración programado de **24 horas**. Cualquier ejecución del script dentro de ese margen leerá los datos locales al instante en lugar de saturar a los proveedores.

3. **Visualizador de Consola (`viewer.py`)**
   - Utiliza la librería `rich` para parsear la caché y generar tablas formateadas directamente en la terminal, separando claramente los proveedores, familias de hardware y métodos de cobro.

## 🛠️ Próximos Pasos (En desarrollo)

El siguiente objetivo para este módulo es la construcción del **Estimador de Circuitos**. 
Una vez definida la fórmula matemática oficial o modelo de IA para calcular el tiempo de ejecución basado en la profundidad (`depth`) de un circuito, se creará el puente que multiplique ese tiempo por estos precios dinámicos, retornando finalmente la métrica de eficiencia `(Costo * Tiempo)` que servirá a QSimplify para optimizar la ejecución.
