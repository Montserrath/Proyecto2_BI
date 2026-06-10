#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crear_dashboards_metabase.py
Proyecto 2 BI - ClickVision Analytics / CercaClick CR

Este archivo crea automaticamente la coleccion, las preguntas y los dashboards
finales en Metabase usando las vistas creadas en PostgreSQL.

Uso recomendado:
    cd ~/Desktop/proyecto2BI/dashboards
    python3 crear_dashboards_metabase.py

El script pregunta correo, contrasena y base de datos de Metabase.
No modifica PostgreSQL. Solo crea elementos dentro de Metabase.
"""

import argparse
import getpass
import json
import sys
import urllib.error
import urllib.request


# ============================================================
# 1. Configuracion general
# ============================================================

NOMBRE_COLECCION = "ClickVision Analytics - CercaClick CR"

# Si ya existen dashboards o preguntas con los mismos nombres dentro de la coleccion,
# el script intenta archivarlos antes de crear la version nueva.
LIMPIAR_ELEMENTOS_ANTERIORES = True

PARAMETRO_PERIODO = {
    "id": "periodo",
    "name": "Periodo analitico",
    "slug": "periodo",
    "type": "category",
}

TEMPLATE_PERIODO = {
    "periodo": {
        "id": "periodo",
        "name": "periodo",
        "display-name": "Periodo analitico",
        "type": "text",
        "required": False,
    }
}


# ============================================================
# 2. Definicion de dashboards y preguntas
# ============================================================

DASHBOARDS = [
    {
        "nombre": "Pregunta 1 - Canales y fuentes de acceso",
        "descripcion": "Analiza cuales canales y fuentes concentran mas sesiones y usuarios nuevos en el sitio.",
        "cards": [
            {
                "nombre": "Sesiones por canal de acceso",
                "display": "bar",
                "sql": """
SELECT
    canal_acceso AS "Canal de acceso",
    SUM(sesiones) AS "Sesiones"
FROM dashboard.vw_p1_canales_fuentes
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY canal_acceso
HAVING SUM(sesiones) > 0
ORDER BY "Sesiones" DESC;
""",
                "pos": (0, 0, 12, 7),
            },
            {
                "nombre": "Sesiones por fuente de acceso",
                "display": "row",
                "sql": """
SELECT
    fuente_acceso AS "Fuente de acceso",
    SUM(sesiones) AS "Sesiones"
FROM dashboard.vw_p1_canales_fuentes
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
  AND LOWER(fuente_acceso) NOT IN ('yahoo', 'newsletter')
GROUP BY fuente_acceso
HAVING SUM(sesiones) > 0
ORDER BY "Sesiones" DESC;
""",
                "pos": (0, 12, 12, 7),
            },
            {
                "nombre": "Participacion porcentual por canal",
                "display": "pie",
                "sql": """
SELECT
    canal_acceso AS "Canal de acceso",
    SUM(sesiones) AS "Sesiones"
FROM dashboard.vw_p1_canales_fuentes
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY canal_acceso
HAVING SUM(sesiones) > 0
ORDER BY "Sesiones" DESC;
""",
                "pos": (7, 0, 12, 7),
            },
            {
                "nombre": "Usuarios nuevos atribuidos por canal de acceso",
                "display": "bar",
                "sql": """
SELECT
    canal_acceso AS "Canal de acceso",
    SUM(usuarios_nuevos) AS "Usuarios nuevos"
FROM dashboard.vw_p1_canales_fuentes
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY canal_acceso
HAVING SUM(usuarios_nuevos) > 0
ORDER BY "Usuarios nuevos" DESC;
""",
                "pos": (7, 12, 12, 7),
            },
            {
                "nombre": "Resumen por canal de acceso",
                "display": "table",
                "sql": """
WITH base AS (
    SELECT
        canal_acceso,
        SUM(sesiones) AS sesiones,
        SUM(usuarios_activos) AS usuarios_activos,
        SUM(usuarios_nuevos) AS usuarios_nuevos
    FROM dashboard.vw_p1_canales_fuentes
    WHERE 1 = 1
    [[AND periodo_analitico = {{periodo}}]]
    GROUP BY canal_acceso
)
SELECT
    canal_acceso AS "Canal de acceso",
    sesiones AS "Sesiones",
    usuarios_activos AS "Usuarios activos",
    usuarios_nuevos AS "Usuarios nuevos",
    ROUND(100.0 * sesiones / NULLIF(SUM(sesiones) OVER (), 0), 2) AS "Participacion de sesiones (%)"
FROM base
WHERE sesiones > 0
ORDER BY sesiones DESC;
""",
                "pos": (14, 0, 24, 8),
            },
        ],
    },
    {
        "nombre": "Pregunta 2 - Interaccion con paginas y recorrido",
        "descripcion": "Resume la interaccion por paginas, tipos de pagina y etapas del recorrido del usuario.",
        "cards": [
            {
                "nombre": "Paginas o secciones con mayor cantidad de vistas",
                "display": "row",
                "sql": """
WITH paginas_limpias AS (
    SELECT
        CASE
            WHEN tipo_pagina = 'Producto' OR es_pagina_producto IN ('Si', 'SI', 'si', 'true', 'True') THEN 'Pagina de producto'
            WHEN LOWER(nombre_pagina) LIKE '%cercaclick%' THEN 'Inicio'
            WHEN nombre_pagina LIKE '/categorias/%' THEN 'Categoria'
            WHEN nombre_pagina LIKE '/ofertas%' THEN 'Ofertas'
            ELSE nombre_pagina
        END AS pagina_seccion,
        vistas
    FROM dashboard.vw_p2_interaccion_recorrido
    WHERE 1 = 1
    [[AND periodo_analitico = {{periodo}}]]
)
SELECT
    pagina_seccion AS "Pagina o seccion",
    SUM(vistas) AS "Vistas"
FROM paginas_limpias
WHERE pagina_seccion IS NOT NULL
  AND pagina_seccion <> 'No identificado'
GROUP BY pagina_seccion
ORDER BY "Vistas" DESC
LIMIT 10;
""",
                "pos": (0, 0, 12, 7),
            },
            {
                "nombre": "Vistas por tipo de pagina",
                "display": "bar",
                "sql": """
SELECT
    tipo_pagina AS "Tipo de pagina",
    SUM(vistas) AS "Vistas"
FROM dashboard.vw_p2_interaccion_recorrido
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY tipo_pagina
ORDER BY "Vistas" DESC;
""",
                "pos": (0, 12, 12, 7),
            },
            {
                "nombre": "Tiempo promedio de interaccion por tipo de pagina (segundos)",
                "display": "bar",
                "sql": """
SELECT
    tipo_pagina AS "Tipo de pagina",
    ROUND(AVG(tiempo_medio_segundos), 2) AS "Tiempo promedio (segundos)"
FROM dashboard.vw_p2_interaccion_recorrido
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY tipo_pagina
ORDER BY "Tiempo promedio (segundos)" DESC;
""",
                "pos": (7, 0, 12, 7),
            },
            {
                "nombre": "Eventos por etapa del recorrido",
                "display": "bar",
                "sql": """
SELECT
    etapa_recorrido AS "Etapa del recorrido",
    SUM(eventos) AS "Eventos"
FROM dashboard.vw_p2_interaccion_recorrido
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY etapa_recorrido
ORDER BY
    CASE etapa_recorrido
        WHEN 'Navegacion general' THEN 1
        WHEN 'Exploracion' THEN 2
        WHEN 'Interes en producto' THEN 3
        WHEN 'Intencion de compra' THEN 4
        WHEN 'Proceso de compra' THEN 5
        WHEN 'Orden generada' THEN 6
        ELSE 99
    END;
""",
                "pos": (7, 12, 12, 7),
            },
            {
                "nombre": "Resumen de interaccion por tipo de pagina",
                "display": "table",
                "sql": """
SELECT
    tipo_pagina AS "Tipo de pagina",
    SUM(vistas) AS "Vistas",
    SUM(eventos) AS "Eventos",
    SUM(eventos_clave) AS "Eventos clave",
    ROUND(AVG(tiempo_medio_segundos), 2) AS "Tiempo promedio (segundos)",
    SUM(impresiones_organicas) AS "Impresiones organicas"
FROM dashboard.vw_p2_interaccion_recorrido
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY tipo_pagina
ORDER BY "Vistas" DESC;
""",
                "pos": (14, 0, 24, 8),
            },
        ],
    },
    {
        "nombre": "Pregunta 3 - Oferta publicada y categorias",
        "descripcion": "Analiza la composicion del catalogo publicado por categoria, precio y valor comercial potencial.",
        "cards": [
            {
                "nombre": "Cantidad de productos por categoria",
                "display": "row",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    SUM(cantidad_productos) AS "Cantidad de productos"
FROM dashboard.vw_p3_oferta_catalogo
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY nombre_categoria
ORDER BY "Cantidad de productos" DESC;
""",
                "pos": (0, 0, 12, 7),
            },
            {
                "nombre": "Precio promedio por categoria",
                "display": "bar",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    ROUND(
        SUM(precio_promedio_usd * cantidad_productos) / NULLIF(SUM(cantidad_productos), 0),
        2
    ) AS "Precio promedio (USD)"
FROM dashboard.vw_p3_oferta_catalogo
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY nombre_categoria
ORDER BY "Precio promedio (USD)" DESC;
""",
                "pos": (0, 12, 12, 7),
            },
            {
                "nombre": "Valor comercial potencial por categoria",
                "display": "row",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    ROUND(SUM(valor_comercial_potencial_usd), 2) AS "Valor comercial potencial (USD)"
FROM dashboard.vw_p3_oferta_catalogo
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY nombre_categoria
ORDER BY "Valor comercial potencial (USD)" DESC;
""",
                "pos": (7, 0, 12, 7),
            },
            {
                "nombre": "Distribucion de productos por rango de precio",
                "display": "bar",
                "sql": """
SELECT
    rango_precio AS "Rango de precio",
    SUM(cantidad_productos) AS "Cantidad de productos"
FROM dashboard.vw_p3_oferta_catalogo
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY rango_precio
ORDER BY
    CASE rango_precio
        WHEN 'Menos de 5 USD' THEN 1
        WHEN 'De 5 a 10 USD' THEN 2
        WHEN 'De 10 a 20 USD' THEN 3
        WHEN 'Mas de 20 USD' THEN 4
        ELSE 99
    END;
""",
                "pos": (7, 12, 12, 7),
            },
            {
                "nombre": "Resumen de oferta por categoria",
                "display": "table",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    SUM(cantidad_productos) AS "Cantidad de productos",
    ROUND(MIN(precio_min_usd), 2) AS "Precio minimo (USD)",
    ROUND(SUM(precio_promedio_usd * cantidad_productos) / NULLIF(SUM(cantidad_productos), 0), 2) AS "Precio promedio (USD)",
    ROUND(MAX(precio_max_usd), 2) AS "Precio maximo (USD)",
    ROUND(SUM(valor_comercial_potencial_usd), 2) AS "Valor comercial potencial (USD)"
FROM dashboard.vw_p3_oferta_catalogo
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY nombre_categoria
ORDER BY "Valor comercial potencial (USD)" DESC;
""",
                "pos": (14, 0, 24, 8),
            },
        ],
    },
    {
        "nombre": "Pregunta 4 - Patrones de actividad por ubicacion y dispositivo",
        "descripcion": "Muestra patrones de actividad segun ubicacion reportada y disponibilidad del dato de dispositivo.",
        "cards": [
            {
                "nombre": "Usuarios activos por ubicacion reportada",
                "display": "row",
                "sql": """
SELECT
    CASE
        WHEN ubicacion_reportada = 'Costa Rica' THEN 'Sin detalle local'
        ELSE ubicacion_reportada
    END AS "Ubicacion reportada",
    SUM(usuarios_activos) AS "Usuarios activos"
FROM dashboard.vw_p4_segmentacion_actividad
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
  AND ubicacion_reportada <> 'No identificado'
  AND (pais = 'Costa Rica' OR es_costa_rica IN ('Si', 'SI', 'si', 'true', 'True'))
GROUP BY 1
ORDER BY "Usuarios activos" DESC
LIMIT 10;
""",
                "pos": (0, 0, 12, 7),
            },
            {
                "nombre": "Usuarios nuevos por pais de procedencia",
                "display": "row",
                "sql": """
SELECT
    CASE
        WHEN pais IS NULL OR pais = '' OR pais = 'No identificado' THEN 'No identificado'
        WHEN pais = 'United States' THEN 'Estados Unidos'
        WHEN pais = 'United Kingdom' THEN 'Reino Unido'
        WHEN pais = 'Spain' THEN 'Espana'
        WHEN pais = 'Mexico' THEN 'Mexico'
        WHEN pais = 'Costa Rica' THEN 'Costa Rica'
        ELSE pais
    END AS "Pais de procedencia",
    SUM(usuarios_nuevos) AS "Usuarios nuevos"
FROM dashboard.vw_p4_segmentacion_actividad
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY 1
HAVING SUM(usuarios_nuevos) > 0
ORDER BY "Usuarios nuevos" DESC
LIMIT 10;
""",
                "pos": (0, 12, 12, 7),
            },
            {
                "nombre": "Nivel de identificacion del dispositivo",
                "display": "pie",
                "sql": """
SELECT
    CASE
        WHEN categoria_dispositivo = 'No identificado' THEN 'Dispositivo no identificado'
        ELSE 'Dispositivo identificado'
    END AS "Nivel de identificacion",
    SUM(usuarios_activos) AS "Usuarios activos"
FROM dashboard.vw_p4_segmentacion_actividad
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
GROUP BY 1
ORDER BY "Usuarios activos" DESC;
""",
                "pos": (7, 0, 12, 7),
            },
            {
                "nombre": "Usuarios activos por dispositivo identificado",
                "display": "bar",
                "sql": """
SELECT
    categoria_dispositivo AS "Tipo de dispositivo",
    SUM(usuarios_activos) AS "Usuarios activos"
FROM dashboard.vw_p4_segmentacion_actividad
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
  AND categoria_dispositivo <> 'No identificado'
GROUP BY categoria_dispositivo
ORDER BY "Usuarios activos" DESC;
""",
                "pos": (7, 12, 12, 7),
            },
            {
                "nombre": "Eventos por ubicacion reportada",
                "display": "row",
                "sql": """
SELECT
    CASE
        WHEN ubicacion_reportada = 'Costa Rica' THEN 'Sin detalle local'
        ELSE ubicacion_reportada
    END AS "Ubicacion reportada",
    SUM(eventos) AS "Eventos"
FROM dashboard.vw_p4_segmentacion_actividad
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
  AND ubicacion_reportada <> 'No identificado'
  AND (pais = 'Costa Rica' OR es_costa_rica IN ('Si', 'SI', 'si', 'true', 'True'))
GROUP BY 1
HAVING SUM(eventos) > 0
ORDER BY "Eventos" DESC
LIMIT 10;
""",
                "pos": (14, 0, 24, 8),
            },
        ],
    },
    {
        "nombre": "Pregunta 5 - Oportunidades comerciales",
        "descripcion": "Cruza oferta publicada con interes registrado para priorizar oportunidades comerciales por categoria.",
        "cards": [
            {
                "nombre": "Matriz de oportunidad por categoria",
                "display": "table",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    cantidad_productos AS "Cantidad de productos",
    valor_comercial_potencial_usd AS "Valor comercial potencial (USD)",
    interacciones_registradas AS "Interacciones registradas",
    interes_promedio_por_producto AS "Interes promedio por producto",
    nivel_oportunidad AS "Nivel de oportunidad",
    accion_sugerida AS "Accion sugerida"
FROM dashboard.vw_p5_oportunidades_comerciales
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
ORDER BY
    CASE nivel_oportunidad
        WHEN 'Alta oportunidad' THEN 1
        WHEN 'Ampliar oferta' THEN 2
        WHEN 'Potenciar visibilidad' THEN 3
        WHEN 'Revisar oferta' THEN 4
        ELSE 5
    END,
    valor_comercial_potencial_usd DESC;
""",
                "pos": (0, 0, 24, 8),
            },
            {
                "nombre": "Oferta publicada vs interes registrado por categoria",
                "display": "bar",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    'Cantidad de productos' AS "Indicador",
    cantidad_productos::numeric AS "Valor"
FROM dashboard.vw_p5_oportunidades_comerciales
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
UNION ALL
SELECT
    nombre_categoria AS "Categoria",
    'Interacciones registradas' AS "Indicador",
    interacciones_registradas::numeric AS "Valor"
FROM dashboard.vw_p5_oportunidades_comerciales
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
ORDER BY "Categoria", "Indicador";
""",
                "pos": (8, 0, 12, 7),
            },
            {
                "nombre": "Producto destacado por categoria",
                "display": "table",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    producto_destacado AS "Producto destacado",
    interacciones_registradas AS "Interacciones registradas",
    precio_promedio_usd AS "Precio promedio (USD)",
    nivel_oportunidad AS "Nivel de oportunidad"
FROM dashboard.vw_p5_oportunidades_comerciales
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
ORDER BY interacciones_registradas DESC, nombre_categoria;
""",
                "pos": (8, 12, 12, 7),
            },
            {
                "nombre": "Valor comercial potencial vs interes registrado",
                "display": "scatter",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    valor_comercial_potencial_usd AS "Valor comercial potencial (USD)",
    interacciones_registradas AS "Interacciones registradas"
FROM dashboard.vw_p5_oportunidades_comerciales
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
ORDER BY valor_comercial_potencial_usd DESC;
""",
                "pos": (15, 0, 12, 7),
            },
            {
                "nombre": "Recomendaciones priorizadas por categoria",
                "display": "table",
                "sql": """
SELECT
    nombre_categoria AS "Categoria",
    nivel_oportunidad AS "Nivel de oportunidad",
    accion_sugerida AS "Accion sugerida",
    cantidad_productos AS "Cantidad de productos",
    valor_comercial_potencial_usd AS "Valor comercial potencial (USD)",
    interacciones_registradas AS "Interacciones registradas"
FROM dashboard.vw_p5_oportunidades_comerciales
WHERE 1 = 1
[[AND periodo_analitico = {{periodo}}]]
ORDER BY
    CASE nivel_oportunidad
        WHEN 'Alta oportunidad' THEN 1
        WHEN 'Ampliar oferta' THEN 2
        WHEN 'Potenciar visibilidad' THEN 3
        WHEN 'Revisar oferta' THEN 4
        ELSE 5
    END,
    interacciones_registradas DESC;
""",
                "pos": (15, 12, 12, 7),
            },
        ],
    },
]



# ============================================================
# 3. Cliente sencillo para la API de Metabase
# ============================================================

class Metabase:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session_id = None

    def request(self, method, path, payload=None):
        url = self.base_url + path
        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["X-Metabase-Session"] = self.session_id

        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                raw = response.read().decode("utf-8")
                if raw.strip() == "":
                    return None
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} en {method} {path}: {detail}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"No se pudo conectar con Metabase en {self.base_url}. Detalle: {e}")

    def login(self, username, password):
        data = self.request("POST", "/api/session", {"username": username, "password": password})
        self.session_id = data["id"]

    def listar_bases(self):
        data = self.request("GET", "/api/database")
        if isinstance(data, dict):
            return data.get("data", [])
        return data or []

    def listar_colecciones(self):
        data = self.request("GET", "/api/collection")
        if isinstance(data, dict):
            return data.get("data", [])
        return data or []

    def crear_coleccion(self, nombre):
        return self.request("POST", "/api/collection", {
            "name": nombre,
            "description": "Coleccion de dashboards finales del Proyecto 2 BI para CercaClick CR.",
            "color": "#509EE3",
        })

    def items_coleccion(self, collection_id):
        data = self.request("GET", f"/api/collection/{collection_id}/items")
        if isinstance(data, dict):
            return data.get("data", [])
        return data or []

    def archivar_card(self, card_id):
        try:
            self.request("DELETE", f"/api/card/{card_id}")
        except Exception as exc:
            print(f"  No se pudo archivar card {card_id}: {exc}")

    def archivar_dashboard(self, dashboard_id):
        try:
            self.request("DELETE", f"/api/dashboard/{dashboard_id}")
        except Exception as exc:
            print(f"  No se pudo archivar dashboard {dashboard_id}: {exc}")

    def crear_card(self, nombre, descripcion, sql, display, database_id, collection_id):
        payload = {
            "name": nombre,
            "description": descripcion,
            "display": display,
            "dataset_query": {
                "database": database_id,
                "type": "native",
                "native": {
                    "query": sql.strip(),
                    "template-tags": TEMPLATE_PERIODO,
                },
            },
            "visualization_settings": configuracion_visual(display),
            "collection_id": collection_id,
        }
        return self.request("POST", "/api/card", payload)

    def crear_dashboard(self, nombre, descripcion, collection_id):
        return self.request("POST", "/api/dashboard", {
            "name": nombre,
            "description": descripcion,
            "parameters": [PARAMETRO_PERIODO],
            "collection_id": collection_id,
        })

    def leer_dashboard(self, dashboard_id):
        return self.request("GET", f"/api/dashboard/{dashboard_id}")

    def actualizar_dashboard(self, dashboard_id, payload):
        return self.request("PUT", f"/api/dashboard/{dashboard_id}", payload)


# ============================================================
# 4. Funciones auxiliares
# ============================================================

def configuracion_visual(display):
    base = {
        "graph.show_values": True,
        "graph.x_axis.axis_enabled": True,
        "graph.y_axis.axis_enabled": True,
    }
    if display == "table":
        return {}
    if display == "pie":
        return {"pie.show_legend": True, "pie.show_total": False}
    if display == "scatter":
        return {"graph.show_values": True}
    return base


def obtener_nombre_item(item):
    return str(item.get("name") or "")


def obtener_tipo_item(item):
    return str(item.get("model") or item.get("type") or item.get("entity_type") or "").lower()


def obtener_id_item(item):
    return item.get("id")


def buscar_o_crear_coleccion(mb):
    for c in mb.listar_colecciones():
        if str(c.get("name")) == NOMBRE_COLECCION:
            print(f"Coleccion encontrada: {NOMBRE_COLECCION}")
            return c["id"]
    creada = mb.crear_coleccion(NOMBRE_COLECCION)
    print(f"Coleccion creada: {NOMBRE_COLECCION}")
    return creada["id"]


def limpiar_elementos_previos(mb, collection_id):
    if not LIMPIAR_ELEMENTOS_ANTERIORES:
        return

    nombres_cards = set()
    nombres_dashboards = {
        "Pregunta 1 - Canales y fuentes de acceso",
        "Pregunta 2 - Interaccion con paginas y recorrido",
        "Pregunta 3 - Oferta publicada y categorias",
        "Pregunta 4 - Segmentacion de actividad",
        "Pregunta 4 - Patrones de actividad por ubicacion y dispositivo",
        "Pregunta 5 - Oportunidades comerciales",
    }
    for dash in DASHBOARDS:
        nombres_dashboards.add(dash["nombre"])
        for card in dash["cards"]:
            nombres_cards.add(card["nombre"])

    prefijos_viejos = ("P1.", "P2.", "P3.", "P4.", "P5.")

    print("Revisando elementos anteriores con nombres viejos o repetidos...")
    for item in mb.items_coleccion(collection_id):
        nombre = obtener_nombre_item(item)
        tipo = obtener_tipo_item(item)
        item_id = obtener_id_item(item)
        if not item_id:
            continue
        if nombre in nombres_dashboards and "dashboard" in tipo:
            print(f"  Archivando dashboard anterior: {nombre}")
            mb.archivar_dashboard(item_id)
        elif (nombre in nombres_cards or nombre.startswith(prefijos_viejos)) and ("card" in tipo or "question" in tipo):
            print(f"  Archivando pregunta anterior: {nombre}")
            mb.archivar_card(item_id)


def elegir_base_datos(mb, database_id_arg=None, database_name_arg=None):
    bases = mb.listar_bases()
    if not bases:
        raise RuntimeError("No se encontraron bases de datos registradas en Metabase.")

    if database_id_arg:
        return int(database_id_arg)

    if database_name_arg:
        for db in bases:
            if str(db.get("name")) == database_name_arg:
                return int(db["id"])
        raise RuntimeError(f"No encontre una base llamada: {database_name_arg}")

    print("\nBases disponibles en Metabase:")
    for db in bases:
        print(f"  {db.get('id')} - {db.get('name')}")

    elegido = input("\nEscribi el ID de la base PostgreSQL que tiene el esquema dashboard: ").strip()
    if not elegido.isdigit():
        raise RuntimeError("El ID de base de datos debe ser numerico.")
    return int(elegido)


def crear_dashcard(card_id, card_def, temp_id):
    row, col, size_x, size_y = card_def["pos"]
    return {
        "id": temp_id,
        "card_id": card_id,
        "row": row,
        "col": col,
        "size_x": size_x,
        "size_y": size_y,
        "parameter_mappings": [
            {
                "parameter_id": "periodo",
                "card_id": card_id,
                "target": ["variable", ["template-tag", "periodo"]],
            }
        ],
        "visualization_settings": {},
    }


def colocar_cards_en_dashboard(mb, dashboard_id, dashboard_name, cards_creadas):
    dashboard = mb.leer_dashboard(dashboard_id)
    dashcards = []
    temp_id = -1

    for card_def, card_id in cards_creadas:
        dashcards.append(crear_dashcard(card_id, card_def, temp_id))
        temp_id -= 1

    payload = {
        "name": dashboard.get("name", dashboard_name),
        "description": dashboard.get("description") or "",
        "parameters": [PARAMETRO_PERIODO],
        "dashcards": dashcards,
    }

    if isinstance(dashboard.get("tabs"), list):
        payload["tabs"] = dashboard.get("tabs")

    mb.actualizar_dashboard(dashboard_id, payload)


# ============================================================
# 5. Ejecucion principal
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Crea dashboards finales de ClickVision en Metabase.")
    parser.add_argument("--metabase-url", default="http://localhost:3000")
    parser.add_argument("--username", default=None)
    parser.add_argument("--database-id", default=None)
    parser.add_argument("--database-name", default=None)
    return parser.parse_args()


def main():
    args = parse_args()

    print("CREACION DE DASHBOARDS - PROYECTO 2 BI")
    print("Metabase:", args.metabase_url)

    username = args.username or input("Correo de Metabase: ").strip()
    password = getpass.getpass("Contrasena de Metabase: ")

    mb = Metabase(args.metabase_url)
    print("Conectando con Metabase...")
    mb.login(username, password)
    print("Sesion iniciada.")

    database_id = elegir_base_datos(mb, args.database_id, args.database_name)
    print(f"Base seleccionada en Metabase: {database_id}")

    collection_id = buscar_o_crear_coleccion(mb)
    limpiar_elementos_previos(mb, collection_id)

    print("\nCreando dashboards y preguntas...")
    total_cards = 0

    for dash in DASHBOARDS:
        print(f"\nDashboard: {dash['nombre']}")
        dashboard = mb.crear_dashboard(dash["nombre"], dash["descripcion"], collection_id)
        dashboard_id = dashboard["id"]

        cards_creadas = []
        for card_def in dash["cards"]:
            card = mb.crear_card(
                nombre=card_def["nombre"],
                descripcion=dash["descripcion"],
                sql=card_def["sql"],
                display=card_def["display"],
                database_id=database_id,
                collection_id=collection_id,
            )
            card_id = card["id"]
            cards_creadas.append((card_def, card_id))
            total_cards += 1
            print(f"  Pregunta creada: {card_def['nombre']}")

        colocar_cards_en_dashboard(mb, dashboard_id, dash["nombre"], cards_creadas)
        print("  Dashboard armado con sus visuales.")

    print("\nProceso terminado.")
    print(f"Dashboards creados: {len(DASHBOARDS)}")
    print(f"Preguntas/cards creadas: {total_cards}")
    print("Abrir Metabase y revisar la coleccion:", NOMBRE_COLECCION)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nERROR:", exc)
        sys.exit(1)
