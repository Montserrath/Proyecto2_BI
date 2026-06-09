-- ============================================================

-- Script 01: creacion del modelo dimensional
-- Este script crea los esquemas, dimensiones y tablas de hechos.

-- ============================================================

DROP SCHEMA IF EXISTS dashboard CASCADE;
DROP SCHEMA IF EXISTS dw CASCADE;

CREATE SCHEMA dw;
CREATE SCHEMA dashboard;

-- ============================================================
-- DIMENSIONES
-- ============================================================

CREATE TABLE dw.dim_tiempo (
    sk_tiempo INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    dia INTEGER,
    mes INTEGER,
    nombre_mes VARCHAR(30),
    anio INTEGER,
    periodo_analitico VARCHAR(80)
);

CREATE TABLE dw.dim_fuente_trafico (
    sk_fuente_trafico INTEGER PRIMARY KEY,
    canal_acceso VARCHAR(120) NOT NULL,
    fuente_acceso VARCHAR(160) NOT NULL,
    medio_original VARCHAR(120)
);

CREATE TABLE dw.dim_pagina (
    sk_pagina INTEGER PRIMARY KEY,
    nombre_pagina VARCHAR(250) NOT NULL,
    tipo_pagina VARCHAR(80) NOT NULL,
    etapa_recorrido VARCHAR(120) NOT NULL,
    es_pagina_producto VARCHAR(10) NOT NULL,
    url_normalizada TEXT
);

CREATE TABLE dw.dim_producto (
    sk_producto INTEGER PRIMARY KEY,
    producto_id_origen VARCHAR(80) NOT NULL,
    nombre_producto TEXT NOT NULL,
    nombre_normalizado TEXT,
    estado_producto VARCHAR(80),
    tipo_catalogo VARCHAR(80)
);

CREATE TABLE dw.dim_categoria (
    sk_categoria INTEGER PRIMARY KEY,
    nombre_categoria VARCHAR(120) NOT NULL
);

CREATE TABLE dw.dim_ubicacion (
    sk_ubicacion INTEGER PRIMARY KEY,
    pais VARCHAR(120) NOT NULL,
    ubicacion_reportada VARCHAR(160) NOT NULL,
    tipo_ubicacion VARCHAR(80),
    es_costa_rica VARCHAR(10)
);

CREATE TABLE dw.dim_dispositivo (
    sk_dispositivo INTEGER PRIMARY KEY,
    categoria_dispositivo VARCHAR(80) NOT NULL
);

-- ============================================================
-- TABLAS DE HECHOS
-- ============================================================

CREATE TABLE dw.fact_acceso_trafico (
    sk_fact_acceso_trafico INTEGER PRIMARY KEY,
    sk_tiempo INTEGER NOT NULL REFERENCES dw.dim_tiempo(sk_tiempo),
    sk_fuente_trafico INTEGER NOT NULL REFERENCES dw.dim_fuente_trafico(sk_fuente_trafico),
    sesiones NUMERIC(14,2) DEFAULT 0 CHECK (sesiones >= 0),
    usuarios_activos NUMERIC(14,2) DEFAULT 0 CHECK (usuarios_activos >= 0),
    usuarios_nuevos NUMERIC(14,2) DEFAULT 0 CHECK (usuarios_nuevos >= 0)
);

CREATE TABLE dw.fact_interaccion_pagina (
    sk_fact_interaccion_pagina INTEGER PRIMARY KEY,
    sk_tiempo INTEGER NOT NULL REFERENCES dw.dim_tiempo(sk_tiempo),
    sk_pagina INTEGER NOT NULL REFERENCES dw.dim_pagina(sk_pagina),
    sk_producto INTEGER NOT NULL REFERENCES dw.dim_producto(sk_producto),
    vistas NUMERIC(14,2) DEFAULT 0 CHECK (vistas >= 0),
    eventos NUMERIC(14,2) DEFAULT 0 CHECK (eventos >= 0),
    eventos_clave NUMERIC(14,2) DEFAULT 0 CHECK (eventos_clave >= 0),
    tiempo_medio_segundos NUMERIC(14,2) DEFAULT 0 CHECK (tiempo_medio_segundos >= 0),
    impresiones_organicas NUMERIC(14,2) DEFAULT 0 CHECK (impresiones_organicas >= 0)
);

CREATE TABLE dw.fact_segmentacion_actividad (
    sk_fact_segmentacion_actividad INTEGER PRIMARY KEY,
    sk_tiempo INTEGER NOT NULL REFERENCES dw.dim_tiempo(sk_tiempo),
    sk_ubicacion INTEGER NOT NULL REFERENCES dw.dim_ubicacion(sk_ubicacion),
    sk_dispositivo INTEGER NOT NULL REFERENCES dw.dim_dispositivo(sk_dispositivo),
    usuarios_activos NUMERIC(14,2) DEFAULT 0 CHECK (usuarios_activos >= 0),
    usuarios_nuevos NUMERIC(14,2) DEFAULT 0 CHECK (usuarios_nuevos >= 0),
    sesiones NUMERIC(14,2) DEFAULT 0 CHECK (sesiones >= 0),
    eventos NUMERIC(14,2) DEFAULT 0 CHECK (eventos >= 0)
);

CREATE TABLE dw.fact_oferta_catalogo (
    sk_fact_oferta_catalogo INTEGER PRIMARY KEY,
    sk_tiempo INTEGER NOT NULL REFERENCES dw.dim_tiempo(sk_tiempo),
    sk_producto INTEGER NOT NULL REFERENCES dw.dim_producto(sk_producto),
    sk_categoria INTEGER NOT NULL REFERENCES dw.dim_categoria(sk_categoria),
    producto_publicado NUMERIC(14,2) DEFAULT 1 CHECK (producto_publicado >= 0),
    precio_usd NUMERIC(14,2) DEFAULT 0 CHECK (precio_usd >= 0),
    valor_comercial_potencial_usd NUMERIC(14,2) DEFAULT 0 CHECK (valor_comercial_potencial_usd >= 0)
);

-- ============================================================
-- INDICES PARA CONSULTA EN DASHBOARD
-- ============================================================

CREATE INDEX idx_fact_acceso_tiempo ON dw.fact_acceso_trafico(sk_tiempo);
CREATE INDEX idx_fact_acceso_fuente ON dw.fact_acceso_trafico(sk_fuente_trafico);

CREATE INDEX idx_fact_interaccion_tiempo ON dw.fact_interaccion_pagina(sk_tiempo);
CREATE INDEX idx_fact_interaccion_pagina ON dw.fact_interaccion_pagina(sk_pagina);
CREATE INDEX idx_fact_interaccion_producto ON dw.fact_interaccion_pagina(sk_producto);

CREATE INDEX idx_fact_segmentacion_tiempo ON dw.fact_segmentacion_actividad(sk_tiempo);
CREATE INDEX idx_fact_segmentacion_ubicacion ON dw.fact_segmentacion_actividad(sk_ubicacion);
CREATE INDEX idx_fact_segmentacion_dispositivo ON dw.fact_segmentacion_actividad(sk_dispositivo);

CREATE INDEX idx_fact_oferta_tiempo ON dw.fact_oferta_catalogo(sk_tiempo);
CREATE INDEX idx_fact_oferta_producto ON dw.fact_oferta_catalogo(sk_producto);
CREATE INDEX idx_fact_oferta_categoria ON dw.fact_oferta_catalogo(sk_categoria);

-- ============================================================
-- Comentarios breves para defensa del modelo
-- ============================================================

COMMENT ON SCHEMA dw IS 'Modelo dimensional final del proyecto ClickVision Analytics / CercaClick CR.';
COMMENT ON SCHEMA dashboard IS 'Vistas analiticas usadas por Metabase para responder las preguntas de negocio.';

COMMENT ON TABLE dw.fact_acceso_trafico IS 'Hecho de acceso al sitio. Grano: fecha y fuente/canal de acceso.';
COMMENT ON TABLE dw.fact_interaccion_pagina IS 'Hecho de interaccion interna. Grano: fecha, pagina y producto cuando aplica.';
COMMENT ON TABLE dw.fact_segmentacion_actividad IS 'Hecho de segmentacion. Grano: fecha, ubicacion reportada y dispositivo.';
COMMENT ON TABLE dw.fact_oferta_catalogo IS 'Hecho de oferta publicada. Grano: fecha de extraccion, producto y categoria.';
