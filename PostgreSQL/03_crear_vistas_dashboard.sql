-- ============================================================
-- Proyecto 2 BI - ClickVision Analytics / CercaClick CR
-- Script 03: vistas analiticas para Metabase
-- Cada vista responde una pregunta de negocio.
-- ============================================================

DROP VIEW IF EXISTS dashboard.vw_p5_oportunidades_comerciales CASCADE;
DROP VIEW IF EXISTS dashboard.vw_p4_segmentacion_actividad CASCADE;
DROP VIEW IF EXISTS dashboard.vw_p3_oferta_catalogo CASCADE;
DROP VIEW IF EXISTS dashboard.vw_p2_interaccion_recorrido CASCADE;
DROP VIEW IF EXISTS dashboard.vw_p1_canales_fuentes CASCADE;

-- ============================================================
-- P1. Canales y fuentes de acceso
-- Pregunta: Cuales canales y fuentes concentran mas sesiones.
-- ============================================================

CREATE VIEW dashboard.vw_p1_canales_fuentes AS
WITH base AS (
    SELECT
        t.anio,
        t.mes,
        t.nombre_mes,
        t.periodo_analitico,
        ft.canal_acceso,
        ft.fuente_acceso,
        ft.medio_original,
        SUM(f.sesiones) AS sesiones,
        SUM(f.usuarios_activos) AS usuarios_activos,
        SUM(f.usuarios_nuevos) AS usuarios_nuevos
    FROM dw.fact_acceso_trafico f
    JOIN dw.dim_tiempo t ON t.sk_tiempo = f.sk_tiempo
    JOIN dw.dim_fuente_trafico ft ON ft.sk_fuente_trafico = f.sk_fuente_trafico
    GROUP BY
        t.anio, t.mes, t.nombre_mes, t.periodo_analitico,
        ft.canal_acceso, ft.fuente_acceso, ft.medio_original
)
SELECT
    anio,
    mes,
    nombre_mes,
    periodo_analitico,
    canal_acceso,
    fuente_acceso,
    medio_original,
    sesiones,
    usuarios_activos,
    usuarios_nuevos,
    ROUND(100.0 * sesiones / NULLIF(SUM(sesiones) OVER (PARTITION BY periodo_analitico), 0), 2) AS porcentaje_sesiones
FROM base;

-- ============================================================
-- P2. Interaccion con paginas, secciones y etapas del recorrido
-- Pregunta: Que paginas, secciones y etapas generan mas interaccion.
-- ============================================================

CREATE VIEW dashboard.vw_p2_interaccion_recorrido AS
SELECT
    t.anio,
    t.mes,
    t.nombre_mes,
    t.periodo_analitico,
    p.nombre_pagina,
    p.tipo_pagina,
    p.etapa_recorrido,
    p.es_pagina_producto,
    p.url_normalizada,
    SUM(f.vistas) AS vistas,
    SUM(f.eventos) AS eventos,
    SUM(f.eventos_clave) AS eventos_clave,
    ROUND(AVG(f.tiempo_medio_segundos), 2) AS tiempo_medio_segundos,
    SUM(f.impresiones_organicas) AS impresiones_organicas
FROM dw.fact_interaccion_pagina f
JOIN dw.dim_tiempo t ON t.sk_tiempo = f.sk_tiempo
JOIN dw.dim_pagina p ON p.sk_pagina = f.sk_pagina
GROUP BY
    t.anio, t.mes, t.nombre_mes, t.periodo_analitico,
    p.nombre_pagina, p.tipo_pagina, p.etapa_recorrido,
    p.es_pagina_producto, p.url_normalizada;

-- ============================================================
-- P3. Oferta publicada por categoria
-- Pregunta: Que categorias concentran mas cantidad, variedad y valor comercial.
-- ============================================================

CREATE VIEW dashboard.vw_p3_oferta_catalogo AS
WITH detalle AS (
    SELECT
        t.anio,
        t.mes,
        t.nombre_mes,
        t.periodo_analitico,
        c.nombre_categoria,
        p.sk_producto,
        p.nombre_producto,
        f.precio_usd,
        f.valor_comercial_potencial_usd,
        CASE
            WHEN f.precio_usd < 5 THEN 'Menos de 5 USD'
            WHEN f.precio_usd >= 5 AND f.precio_usd < 10 THEN 'De 5 a 10 USD'
            WHEN f.precio_usd >= 10 AND f.precio_usd < 20 THEN 'De 10 a 20 USD'
            ELSE 'Mas de 20 USD'
        END AS rango_precio
    FROM dw.fact_oferta_catalogo f
    JOIN dw.dim_tiempo t ON t.sk_tiempo = f.sk_tiempo
    JOIN dw.dim_producto p ON p.sk_producto = f.sk_producto
    JOIN dw.dim_categoria c ON c.sk_categoria = f.sk_categoria
    WHERE COALESCE(p.tipo_catalogo, '') <> 'Usados variados'
)
SELECT
    anio,
    mes,
    nombre_mes,
    periodo_analitico,
    nombre_categoria,
    rango_precio,
    COUNT(DISTINCT sk_producto) AS cantidad_productos,
    ROUND(MIN(precio_usd), 2) AS precio_min_usd,
    ROUND(AVG(precio_usd), 2) AS precio_promedio_usd,
    ROUND(MAX(precio_usd), 2) AS precio_max_usd,
    ROUND(SUM(valor_comercial_potencial_usd), 2) AS valor_comercial_potencial_usd
FROM detalle
GROUP BY
    anio, mes, nombre_mes, periodo_analitico,
    nombre_categoria, rango_precio;

-- ============================================================
-- P4. Segmentacion por ubicacion reportada y dispositivo
-- Pregunta: Donde y desde que dispositivos se concentra la actividad.
-- ============================================================

CREATE VIEW dashboard.vw_p4_segmentacion_actividad AS
SELECT
    t.anio,
    t.mes,
    t.nombre_mes,
    t.periodo_analitico,
    u.pais,
    u.ubicacion_reportada,
    u.tipo_ubicacion,
    u.es_costa_rica,
    d.categoria_dispositivo,
    SUM(f.usuarios_activos) AS usuarios_activos,
    SUM(f.usuarios_nuevos) AS usuarios_nuevos,
    SUM(f.sesiones) AS sesiones,
    SUM(f.eventos) AS eventos
FROM dw.fact_segmentacion_actividad f
JOIN dw.dim_tiempo t ON t.sk_tiempo = f.sk_tiempo
JOIN dw.dim_ubicacion u ON u.sk_ubicacion = f.sk_ubicacion
JOIN dw.dim_dispositivo d ON d.sk_dispositivo = f.sk_dispositivo
GROUP BY
    t.anio, t.mes, t.nombre_mes, t.periodo_analitico,
    u.pais, u.ubicacion_reportada, u.tipo_ubicacion, u.es_costa_rica,
    d.categoria_dispositivo;

-- ============================================================
-- P5. Oportunidades comerciales
-- Pregunta: Que categorias presentan mayor oportunidad comercial al comparar
-- oferta publicada con interes registrado por los usuarios.
-- ============================================================

CREATE VIEW dashboard.vw_p5_oportunidades_comerciales AS
WITH oferta AS (
    SELECT
        t.periodo_analitico,
        c.sk_categoria,
        c.nombre_categoria,
        COUNT(DISTINCT p.sk_producto) AS cantidad_productos,
        ROUND(SUM(f.valor_comercial_potencial_usd), 2) AS valor_comercial_potencial_usd,
        ROUND(AVG(f.precio_usd), 2) AS precio_promedio_usd
    FROM dw.fact_oferta_catalogo f
    JOIN dw.dim_tiempo t ON t.sk_tiempo = f.sk_tiempo
    JOIN dw.dim_producto p ON p.sk_producto = f.sk_producto
    JOIN dw.dim_categoria c ON c.sk_categoria = f.sk_categoria
    WHERE COALESCE(p.tipo_catalogo, '') <> 'Usados variados'
    GROUP BY t.periodo_analitico, c.sk_categoria, c.nombre_categoria
),
interes_producto AS (
    SELECT
        fi.sk_producto,
        SUM(fi.vistas + fi.eventos + fi.eventos_clave) AS interacciones_registradas,
        SUM(fi.vistas) AS vistas_registradas,
        SUM(fi.eventos_clave) AS eventos_clave
    FROM dw.fact_interaccion_pagina fi
    GROUP BY fi.sk_producto
),
interes_categoria AS (
    SELECT
        t.periodo_analitico,
        c.sk_categoria,
        SUM(COALESCE(ip.interacciones_registradas, 0)) AS interacciones_registradas,
        SUM(COALESCE(ip.vistas_registradas, 0)) AS vistas_registradas,
        SUM(COALESCE(ip.eventos_clave, 0)) AS eventos_clave
    FROM dw.fact_oferta_catalogo fo
    JOIN dw.dim_tiempo t ON t.sk_tiempo = fo.sk_tiempo
    JOIN dw.dim_producto p ON p.sk_producto = fo.sk_producto
    JOIN dw.dim_categoria c ON c.sk_categoria = fo.sk_categoria
    LEFT JOIN interes_producto ip ON ip.sk_producto = p.sk_producto
    WHERE COALESCE(p.tipo_catalogo, '') <> 'Usados variados'
    GROUP BY t.periodo_analitico, c.sk_categoria
),
producto_top AS (
    SELECT
        periodo_analitico,
        sk_categoria,
        nombre_producto AS producto_destacado
    FROM (
        SELECT
            t.periodo_analitico,
            c.sk_categoria,
            p.nombre_producto,
            COALESCE(ip.interacciones_registradas, 0) AS interacciones_producto,
            ROW_NUMBER() OVER (
                PARTITION BY t.periodo_analitico, c.sk_categoria
                ORDER BY COALESCE(ip.interacciones_registradas, 0) DESC, p.nombre_producto
            ) AS rn
        FROM dw.fact_oferta_catalogo fo
        JOIN dw.dim_tiempo t ON t.sk_tiempo = fo.sk_tiempo
        JOIN dw.dim_producto p ON p.sk_producto = fo.sk_producto
        JOIN dw.dim_categoria c ON c.sk_categoria = fo.sk_categoria
        LEFT JOIN interes_producto ip ON ip.sk_producto = p.sk_producto
        WHERE COALESCE(p.tipo_catalogo, '') <> 'Usados variados'
    ) x
    WHERE rn = 1
),
base AS (
    SELECT
        o.periodo_analitico,
        o.nombre_categoria,
        o.cantidad_productos,
        o.valor_comercial_potencial_usd,
        o.precio_promedio_usd,
        COALESCE(i.interacciones_registradas, 0) AS interacciones_registradas,
        COALESCE(i.vistas_registradas, 0) AS vistas_registradas,
        COALESCE(i.eventos_clave, 0) AS eventos_clave,
        ROUND(COALESCE(i.interacciones_registradas, 0) / NULLIF(o.cantidad_productos, 0), 2) AS interes_promedio_por_producto,
        pt.producto_destacado
    FROM oferta o
    LEFT JOIN interes_categoria i
        ON i.periodo_analitico = o.periodo_analitico
       AND i.sk_categoria = o.sk_categoria
    LEFT JOIN producto_top pt
        ON pt.periodo_analitico = o.periodo_analitico
       AND pt.sk_categoria = o.sk_categoria
),
promedios AS (
    SELECT
        AVG(interacciones_registradas) AS promedio_interacciones,
        AVG(valor_comercial_potencial_usd) AS promedio_valor,
        AVG(cantidad_productos) AS promedio_productos
    FROM base
)
SELECT
    b.periodo_analitico,
    b.nombre_categoria,
    b.cantidad_productos,
    b.valor_comercial_potencial_usd,
    b.precio_promedio_usd,
    b.interacciones_registradas,
    b.vistas_registradas,
    b.eventos_clave,
    b.interes_promedio_por_producto,
    b.producto_destacado,
    CASE
        WHEN b.interacciones_registradas >= p.promedio_interacciones
         AND b.valor_comercial_potencial_usd >= p.promedio_valor
            THEN 'Alta oportunidad'
        WHEN b.interacciones_registradas >= p.promedio_interacciones
         AND b.cantidad_productos < p.promedio_productos
            THEN 'Ampliar oferta'
        WHEN b.valor_comercial_potencial_usd >= p.promedio_valor
         AND b.interacciones_registradas < p.promedio_interacciones
            THEN 'Potenciar visibilidad'
        WHEN b.cantidad_productos >= p.promedio_productos
         AND b.interacciones_registradas < p.promedio_interacciones
            THEN 'Revisar oferta'
        ELSE 'Monitorear'
    END AS nivel_oportunidad,
    CASE
        WHEN b.interacciones_registradas >= p.promedio_interacciones
         AND b.valor_comercial_potencial_usd >= p.promedio_valor
            THEN 'Priorizar exposicion y seguimiento comercial'
        WHEN b.interacciones_registradas >= p.promedio_interacciones
         AND b.cantidad_productos < p.promedio_productos
            THEN 'Evaluar incorporacion de productos similares'
        WHEN b.valor_comercial_potencial_usd >= p.promedio_valor
         AND b.interacciones_registradas < p.promedio_interacciones
            THEN 'Mejorar visibilidad dentro del sitio'
        WHEN b.cantidad_productos >= p.promedio_productos
         AND b.interacciones_registradas < p.promedio_interacciones
            THEN 'Revisar atractivo, ubicacion o presentacion de la oferta'
        ELSE 'Dar seguimiento en proximas mediciones'
    END AS accion_sugerida
FROM base b
CROSS JOIN promedios p;
