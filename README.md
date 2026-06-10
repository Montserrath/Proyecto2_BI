Proyecto BI - ClickVision Analytics
Problema

CercaClickr.com es una plataforma digital orientada a la publicación y consulta de productos mediante un modelo tipo marketplace. Aunque la organización dispone de información proveniente de diferentes fuentes, como Google Analytics 4 y registros asociados al catálogo de productos, gran parte de estos datos se encuentran dispersos y sin una estructura unificada que facilite su análisis.

La organización requiere comprender mejor el comportamiento de los usuarios dentro de la plataforma, identificar las principales fuentes de acceso, analizar los patrones de interacción con páginas y productos, así como evaluar oportunidades comerciales a partir de la actividad registrada. Asimismo, resulta importante conocer cómo se distribuye el tráfico según ubicación geográfica y tipo de dispositivo, permitiendo obtener una visión más completa del desempeño de la plataforma.

El problema no se encuentra en la ausencia de información, sino en la falta de una solución que permita integrar, organizar y analizar los datos de manera consistente. Mientras esta situación persista, será más difícil transformar los datos disponibles en información útil para apoyar la toma de decisiones.

Arquitectura de la solución

La solución implementada sigue un enfoque de Business Intelligence basado en una arquitectura dimensional.

Fuente de datos (Origen operacional)

La información utilizada proviene de archivos estructurados generados a partir de Google Analytics 4 y del catálogo de productos de CercaClickr.com. Estas fuentes contienen información relacionada con tráfico, interacción de usuarios, segmentación de actividad y oferta publicada.

Proceso ETL (Apache Hop)

Se desarrolló un proceso ETL compuesto por dos pipelines principales. El primero realiza tareas de staging, limpieza y validación de datos, mientras que el segundo transforma la información validada hacia un modelo dimensional. Durante este proceso se aplican reglas de normalización, control de calidad y generación de estructuras analíticas.

Data Warehouse (PostgreSQL)

Se implementó un almacén de datos basado en una constelación de hechos compuesta por cuatro tablas de hechos:

fact_acceso_trafico
fact_interaccion_pagina
fact_segmentacion_actividad
fact_oferta_catalogo

Además, se construyeron siete dimensiones:

dim_tiempo
dim_fuente_trafico
dim_pagina
dim_producto
dim_categoria
dim_ubicacion
dim_dispositivo
Análisis y visualización (Metabase)

Se desarrollaron cinco dashboards analíticos orientados a responder las preguntas de negocio definidas para el proyecto. Los dashboards permiten analizar:

Fuentes de acceso y comportamiento del tráfico.
Interacción de usuarios con páginas y productos.
Segmentación de actividad por ubicación geográfica.
Distribución de actividad según dispositivo utilizado.
Oferta publicada y oportunidades comerciales.
Indicadores clave para apoyar la toma de decisiones.
Integrantes del grupo
David Acuña Brenes
Esteban Brenes Montoya
Valery Fonseca Cerdas
Monserrat Martínez González
Randall Sánchez Ortiz
Pablo Solís Valverde
Instrucciones de ejecución
Ejecución del proceso ETL
Abrir Apache Hop.
Ejecutar el workflow principal:
00_workflow_proyecto2_bi.hwf
El workflow ejecutará automáticamente los siguientes pipelines:
01_staging_validacion.hpl
02_modelo_dimensional.hpl
Al finalizar el proceso se generarán los datos necesarios para la construcción del modelo dimensional y su posterior carga en PostgreSQL.
Implementación del almacén de datos en PostgreSQL

Ejecutar los scripts en el siguiente orden:

01_crear_tablas_dw.sql
02_insertar_datos_dw_pgadmin.sql
03_crear_vistas_dashboard.sql
04_validaciones_modelo.sql
Visualización de resultados

Una vez cargado el almacén de datos, configurar la conexión desde Metabase hacia PostgreSQL para acceder a los dashboards y consultas analíticas desarrolladas durante el proyecto.

Herramientas utilizadas
Apache Hop
PostgreSQL
Metabase
GitHub
Estructura del repositorio
/Documentacion
│
├── Proyecto_2_BI.pdf
├── Presentacion_Final.pdf
│
/ApacheHop
│
├── 00_workflow_proyecto2_bi.hwf
├── 01_staging_validacion.hpl
├── 02_modelo_dimensional.hpl
│
/PostgreSQL
│
├── 01_crear_tablas_dw.sql
├── 02_insertar_datos_dw_pgadmin.sql
├── 03_crear_vistas_dashboard.sql
├── 04_validaciones_modelo.sql
│
/Diagramas
│
├── Modelo_Operacional.png
├── Arquitectura_BI.png
├── Modelo_Dimensional.png
│
