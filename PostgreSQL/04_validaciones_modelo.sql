-- ============================================================
-- Proyecto 2 BI - ClickVision Analytics / CercaClick CR
-- Script 04: validaciones del modelo dimensional y vistas
-- Este archivo sirve como evidencia de control despues de la carga.
-- ============================================================

-- Conteo general de tablas del modelo
SELECT 'dim_tiempo' AS objeto, COUNT(*) AS registros FROM dw.dim_tiempo
UNION ALL SELECT 'dim_fuente_trafico', COUNT(*) FROM dw.dim_fuente_trafico
UNION ALL SELECT 'dim_pagina', COUNT(*) FROM dw.dim_pagina
UNION ALL SELECT 'dim_producto', COUNT(*) FROM dw.dim_producto
UNION ALL SELECT 'dim_categoria', COUNT(*) FROM dw.dim_categoria
UNION ALL SELECT 'dim_ubicacion', COUNT(*) FROM dw.dim_ubicacion
UNION ALL SELECT 'dim_dispositivo', COUNT(*) FROM dw.dim_dispositivo
UNION ALL SELECT 'fact_acceso_trafico', COUNT(*) FROM dw.fact_acceso_trafico
UNION ALL SELECT 'fact_interaccion_pagina', COUNT(*) FROM dw.fact_interaccion_pagina
UNION ALL SELECT 'fact_segmentacion_actividad', COUNT(*) FROM dw.fact_segmentacion_actividad
UNION ALL SELECT 'fact_oferta_catalogo', COUNT(*) FROM dw.fact_oferta_catalogo
ORDER BY objeto;

-- Verificacion de medidas negativas. Debe devolver 0 en todos los casos.
SELECT 'fact_acceso_trafico_sesiones_negativas' AS validacion, COUNT(*) AS registros
FROM dw.fact_acceso_trafico WHERE sesiones < 0
UNION ALL
SELECT 'fact_interaccion_vistas_negativas', COUNT(*)
FROM dw.fact_interaccion_pagina WHERE vistas < 0
UNION ALL
SELECT 'fact_segmentacion_usuarios_negativos', COUNT(*)
FROM dw.fact_segmentacion_actividad WHERE usuarios_activos < 0 OR usuarios_nuevos < 0
UNION ALL
SELECT 'fact_oferta_precio_negativo', COUNT(*)
FROM dw.fact_oferta_catalogo WHERE precio_usd < 0;

-- Verificacion de llaves huerfanas. Debe devolver 0 en todos los casos.
SELECT 'acceso_sin_tiempo' AS validacion, COUNT(*) AS registros
FROM dw.fact_acceso_trafico f LEFT JOIN dw.dim_tiempo d ON d.sk_tiempo = f.sk_tiempo
WHERE d.sk_tiempo IS NULL
UNION ALL
SELECT 'acceso_sin_fuente', COUNT(*)
FROM dw.fact_acceso_trafico f LEFT JOIN dw.dim_fuente_trafico d ON d.sk_fuente_trafico = f.sk_fuente_trafico
WHERE d.sk_fuente_trafico IS NULL
UNION ALL
SELECT 'interaccion_sin_pagina', COUNT(*)
FROM dw.fact_interaccion_pagina f LEFT JOIN dw.dim_pagina d ON d.sk_pagina = f.sk_pagina
WHERE d.sk_pagina IS NULL
UNION ALL
SELECT 'interaccion_sin_producto', COUNT(*)
FROM dw.fact_interaccion_pagina f LEFT JOIN dw.dim_producto d ON d.sk_producto = f.sk_producto
WHERE d.sk_producto IS NULL
UNION ALL
SELECT 'segmentacion_sin_ubicacion', COUNT(*)
FROM dw.fact_segmentacion_actividad f LEFT JOIN dw.dim_ubicacion d ON d.sk_ubicacion = f.sk_ubicacion
WHERE d.sk_ubicacion IS NULL
UNION ALL
SELECT 'segmentacion_sin_dispositivo', COUNT(*)
FROM dw.fact_segmentacion_actividad f LEFT JOIN dw.dim_dispositivo d ON d.sk_dispositivo = f.sk_dispositivo
WHERE d.sk_dispositivo IS NULL
UNION ALL
SELECT 'oferta_sin_categoria', COUNT(*)
FROM dw.fact_oferta_catalogo f LEFT JOIN dw.dim_categoria d ON d.sk_categoria = f.sk_categoria
WHERE d.sk_categoria IS NULL
UNION ALL
SELECT 'oferta_sin_producto', COUNT(*)
FROM dw.fact_oferta_catalogo f LEFT JOIN dw.dim_producto d ON d.sk_producto = f.sk_producto
WHERE d.sk_producto IS NULL;

-- Validacion de vistas para dashboard. Todas deben tener registros.
SELECT 'vw_p1_canales_fuentes' AS vista, COUNT(*) AS registros FROM dashboard.vw_p1_canales_fuentes
UNION ALL SELECT 'vw_p2_interaccion_recorrido', COUNT(*) FROM dashboard.vw_p2_interaccion_recorrido
UNION ALL SELECT 'vw_p3_oferta_catalogo', COUNT(*) FROM dashboard.vw_p3_oferta_catalogo
UNION ALL SELECT 'vw_p4_segmentacion_actividad', COUNT(*) FROM dashboard.vw_p4_segmentacion_actividad
UNION ALL SELECT 'vw_p5_oportunidades_comerciales', COUNT(*) FROM dashboard.vw_p5_oportunidades_comerciales
ORDER BY vista;

-- Revision de valores no identificados. No necesariamente es error, pero sirve para documentar limitaciones.
SELECT 'ubicacion_no_identificada' AS control, COUNT(*) AS registros
FROM dw.dim_ubicacion
WHERE LOWER(ubicacion_reportada) = 'no identificado'
UNION ALL
SELECT 'dispositivo_no_identificado', COUNT(*)
FROM dw.dim_dispositivo
WHERE LOWER(categoria_dispositivo) = 'no identificado'
UNION ALL
SELECT 'fuente_no_identificada', COUNT(*)
FROM dw.dim_fuente_trafico
WHERE LOWER(fuente_acceso) = 'no identificado';
