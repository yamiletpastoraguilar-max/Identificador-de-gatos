"""Almacenamiento en SQLite (datos + fotos)."""
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

DB_PATH = os.environ.get("GATOS_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "gatos.db"))
TZ = ZoneInfo("America/Lima")

CAMPOS = [
    "registrado_por", "lugar", "pelaje_predominante", "pelaje_detalle", "sexo", "gestacion",
    "estado_sanitario", "estado_sanitario_detalle", "edad", "condicion_corporal",
    "condicion_detalle", "tamano", "info_adicional",
]


@contextmanager
def conexion():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    with conexion() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS gatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT,
                fecha TEXT NOT NULL,
                registrado_por TEXT, lugar TEXT, pelaje_predominante TEXT, pelaje_detalle TEXT,
                sexo TEXT, gestacion TEXT, estado_sanitario TEXT, estado_sanitario_detalle TEXT,
                edad TEXT, condicion_corporal TEXT, condicion_detalle TEXT, tamano TEXT,
                info_adicional TEXT
            );
            CREATE TABLE IF NOT EXISTS fotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gato_id INTEGER NOT NULL REFERENCES gatos(id) ON DELETE CASCADE,
                imagen BLOB NOT NULL
            );
            """
        )


def insertar(datos: dict, fotos: list[bytes]) -> str:
    fecha = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    cols = ["fecha"] + CAMPOS
    vals = [fecha] + [datos.get(c, "") for c in CAMPOS]
    with conexion() as con:
        cur = con.execute(
            f"INSERT INTO gatos ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})", vals
        )
        gid = cur.lastrowid
        codigo = f"GATO-{gid:04d}"
        con.execute("UPDATE gatos SET codigo = ? WHERE id = ?", (codigo, gid))
        con.executemany("INSERT INTO fotos (gato_id, imagen) VALUES (?, ?)", [(gid, f) for f in fotos])
    return codigo


def listar() -> pd.DataFrame:
    with conexion() as con:
        return pd.read_sql_query("SELECT * FROM gatos ORDER BY id DESC", con)


def fotos_de(gato_id: int) -> list[bytes]:
    with conexion() as con:
        return [r[0] for r in con.execute("SELECT imagen FROM fotos WHERE gato_id = ? ORDER BY id", (gato_id,))]


def primeras_fotos() -> dict[int, bytes]:
    with conexion() as con:
        rows = con.execute("SELECT gato_id, imagen FROM fotos ORDER BY id").fetchall()
    out: dict[int, bytes] = {}
    for gid, img in rows:
        out.setdefault(gid, img)
    return out


def eliminar(gato_id: int):
    with conexion() as con:
        con.execute("DELETE FROM fotos WHERE gato_id = ?", (gato_id,))
        con.execute("DELETE FROM gatos WHERE id = ?", (gato_id,))


def respaldo_bytes() -> bytes:
    with open(DB_PATH, "rb") as f:
        return f.read()


def restaurar(data: bytes):
    """Reemplaza la base de datos por una copia de seguridad (valida su estructura)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(data)
        ruta = tmp.name
    try:
        con = sqlite3.connect(ruta)
        tablas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        con.close()
        if not {"gatos", "fotos"} <= tablas:
            raise ValueError("El archivo no es una copia de seguridad válida de este programa.")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        os.replace(ruta, DB_PATH)
    finally:
        if os.path.exists(ruta):
            os.remove(ruta)
