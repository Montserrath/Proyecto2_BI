Carpeta de datos - Proyecto 2 BI

Esta carpeta contiene los archivos de origen que alimentan el ETL del proyecto ClickVision Analytics / CercaClick CR.

Ajustes realizados:
- Se eliminaron tildes y caracteres especiales en nombres de archivos y contenido.
- Se mantuvo la estructura general de los CSV originales.
- No se crearon dimensiones ni tablas de hechos en esta carpeta; ese trabajo queda para el ETL.
- Se elimino basura tecnica de macOS como __MACOSX y .DS_Store.
- Se conserva catalogo_productos_origen.csv como fuente operacional necesaria para responder las preguntas sobre oferta, categorias y oportunidades comerciales.

Uso esperado:
1. Copiar esta carpeta datos dentro de proyecto2BI.
2. Ejecutar el Pipeline 1 para crear archivos staging.
3. Ejecutar el Pipeline 2 para construir dimensiones y tablas de hechos.
