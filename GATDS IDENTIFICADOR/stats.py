"""Tablas de conteo usadas en pantalla y en el Excel."""
import pandas as pd

import config as C


def _conteo(serie: pd.Series, categorias: list[str]) -> pd.DataFrame:
    c = serie.value_counts()
    return pd.DataFrame({"Categoría": categorias, "Cantidad": [int(c.get(k, 0)) for k in categorias]})


def tablas(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    vacio = pd.Series(dtype=str)
    col = lambda n: df[n] if len(df) else vacio

    sanitario = col("estado_sanitario").str.split("; ").explode() if len(df) else vacio
    hembras = df[df["sexo"] == "Hembra"] if len(df) else df
    gest = hembras["gestacion"] if len(df) else vacio

    lugares = col("lugar").str.strip().str.title()
    top = lugares.value_counts().head(15)
    t_lugar = pd.DataFrame({"Categoría": list(top.index), "Cantidad": [int(v) for v in top.values]})

    dias = col("fecha").str[:10].value_counts().sort_index()
    t_dias = pd.DataFrame({"Categoría": list(dias.index), "Cantidad": [int(v) for v in dias.values]})

    return {
        "Color de pelaje predominante": _conteo(col("pelaje_predominante"), C.PELAJES),
        "Sexo aparente": _conteo(col("sexo"), C.SEXOS),
        "Gestación (solo hembras)": _conteo(gest, C.GESTACION),
        "Estado sanitario visible (un gato puede tener varios)": _conteo(sanitario, C.SANITARIO),
        "Edad aparente": _conteo(col("edad"), C.EDADES),
        "Condición corporal": _conteo(col("condicion_corporal"), C.CONDICIONES),
        "Tamaño aproximado": _conteo(col("tamano"), C.TAMANOS),
        "Lugar donde se vio (máx. 15)": t_lugar,
        "Gatos registrados por fecha": t_dias,
    }
