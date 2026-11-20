"""
🐱 Registro de Gatos
Gestor de información: registra gatos con fotos y datos, y exporta todo a Excel con gráficos.
Ejecutar: streamlit run app.py
"""
import io
import os
from datetime import datetime

import altair as alt
import streamlit as st
from PIL import Image, ImageOps

import config as C
import db
import stats
from excel_export import construir_excel

st.set_page_config(page_title="Registro de Gatos", page_icon="🐱", layout="wide")
db.init_db()


# ------------------------------ utilidades ------------------------------
def preparar_foto(archivo) -> bytes:
    img = ImageOps.exif_transpose(Image.open(archivo)).convert("RGB")
    img.thumbnail((1024, 1024))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def clave_admin() -> str | None:
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return os.environ.get("ADMIN_PASSWORD")


def pedir_clave(key: str) -> bool:
    """Devuelve True si no hay clave configurada o si la ingresada es correcta."""
    esperada = clave_admin()
    if not esperada:
        return True
    return st.text_input("Clave de administrador", type="password", key=key) == esperada


def grafico(t):
    return (
        alt.Chart(t)
        .mark_bar()
        .encode(
            y=alt.Y("Categoría:N", sort=None, title=None),
            x=alt.X("Cantidad:Q", title="Cantidad de gatos", axis=alt.Axis(tickMinStep=1)),
            tooltip=["Categoría", "Cantidad"],
        )
        .properties(height=max(120, 34 * len(t)))
    )


# ------------------------------ interfaz ------------------------------
st.title("🐱 Registro de Gatos")
st.caption("Registra gatos con fotos, completa sus datos y descarga todo en Excel con gráficos.")

tab_reg, tab_lista, tab_stats, tab_export = st.tabs(
    ["➕ Registrar", "📋 Registros", "📊 Estadísticas", "📥 Excel y respaldo"]
)

# ------------------------------ 1. Registrar ------------------------------
with tab_reg:
    n = st.session_state.setdefault("form_n", 0)
    k = lambda nombre: f"{nombre}_{n}"  # al cambiar n se limpia el formulario

    if msg := st.session_state.pop("msg_ok", None):
        st.success(msg)

    st.subheader("1. Fotos del gato")
    subidas = st.file_uploader(
        "Sube hasta 3 fotos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key=k("fotos")
    )
    foto_cam = None
    if st.toggle("📷 Tomar foto con la cámara", key=k("cam_on")):
        foto_cam = st.camera_input("Cámara", key=k("cam"))

    st.subheader("2. Datos del gato")
    c1, c2 = st.columns(2)
    with c1:
        lugar = st.text_input("📍 ¿En qué lugar se vio? *", placeholder="Ej.: Parque Zela, Tacna", key=k("lugar"))
        pelaje = st.selectbox(
            "Color de pelaje predominante *", C.PELAJES, index=None, placeholder="Selecciona...", key=k("pelaje")
        )
        pelaje_detalle = ""
        if pelaje == "Combinación de colores":
            pelaje_detalle = st.text_input(
                "Especifica la combinación de colores *", placeholder="Ej.: blanco con manchas negras", key=k("pdet")
            )
        sexo = st.radio("Sexo aparente *", C.SEXOS, index=None, horizontal=True, key=k("sexo"))
        gestacion = ""
        if sexo == "Hembra":
            gestacion = st.radio("¿Está en gestación? *", C.GESTACION, index=None, horizontal=True, key=k("gest"))
    with c2:
        edad = st.selectbox("Edad aparente *", C.EDADES, index=None, placeholder="Selecciona...", key=k("edad"))
        condicion = st.selectbox(
            "Condición corporal *", C.CONDICIONES, index=None, placeholder="Selecciona...", key=k("cond")
        )
        condicion_detalle = ""
        if condicion == "Otro":
            condicion_detalle = st.text_input("Especifica la condición corporal *", key=k("cdet"))
        tamano = st.selectbox(
            "Tamaño aproximado *", C.TAMANOS, index=None, placeholder="Selecciona...", key=k("tam")
        )

    sanitario = st.multiselect(
        "Estado sanitario visible * (puedes marcar varios)", C.SANITARIO, key=k("san"),
        placeholder="Selecciona una o más opciones",
    )
    sanitario_detalle = st.text_input(
        "Detalle del estado sanitario (opcional)", placeholder="Ej.: herida en la oreja izquierda", key=k("sdet")
    )
    info = st.text_area("Información adicional (opcional)", key=k("info"),
                        placeholder="Comportamiento, collar, oreja cortada, si lo alimenta alguien, etc.")
    registrado_por = st.text_input("Registrado por (opcional)", key=k("por"))

    if st.button("💾 Guardar registro", type="primary"):
        fotos_in = list(subidas or [])[:3]
        if foto_cam is not None:
            fotos_in.append(foto_cam)
        errores = []
        if not fotos_in:
            errores.append("Agrega al menos una foto.")
        if not lugar.strip():
            errores.append("Indica el lugar donde se vio.")
        if not pelaje:
            errores.append("Selecciona el color de pelaje predominante.")
        if pelaje == "Combinación de colores" and not pelaje_detalle.strip():
            errores.append("Especifica la combinación de colores.")
        if not sexo:
            errores.append("Selecciona el sexo aparente.")
        if sexo == "Hembra" and not gestacion:
            errores.append("Indica si la hembra está en gestación.")
        if not sanitario:
            errores.append("Selecciona el estado sanitario visible.")
        if not edad:
            errores.append("Selecciona la edad aparente.")
        if not condicion:
            errores.append("Selecciona la condición corporal.")
        if condicion == "Otro" and not condicion_detalle.strip():
            errores.append("Especifica la condición corporal.")
        if not tamano:
            errores.append("Selecciona el tamaño aproximado.")

        if errores:
            for e in errores:
                st.error(e)
        else:
            codigo = db.insertar(
                {
                    "registrado_por": registrado_por.strip(),
                    "lugar": lugar.strip(),
                    "pelaje_predominante": pelaje,
                    "pelaje_detalle": pelaje_detalle.strip(),
                    "sexo": sexo,
                    "gestacion": gestacion if sexo == "Hembra" else "",
                    "estado_sanitario": "; ".join(sanitario),
                    "estado_sanitario_detalle": sanitario_detalle.strip(),
                    "edad": edad,
                    "condicion_corporal": condicion,
                    "condicion_detalle": condicion_detalle.strip(),
                    "tamano": tamano,
                    "info_adicional": info.strip(),
                },
                [preparar_foto(f) for f in fotos_in],
            )
            st.session_state["msg_ok"] = f"✅ Gato registrado con el código **{codigo}**."
            st.session_state["form_n"] = n + 1
            st.rerun()

# ------------------------------ 2. Registros ------------------------------
with tab_lista:
    df = db.listar()
    if df.empty:
        st.info("Aún no hay gatos registrados.")
    else:
        f1, f2, f3, f4 = st.columns(4)
        fs = f1.multiselect("Sexo", C.SEXOS)
        fe = f2.multiselect("Edad", C.EDADES)
        fp = f3.multiselect("Pelaje", C.PELAJES)
        fl = f4.text_input("Buscar lugar")
        vista = df
        if fs:
            vista = vista[vista["sexo"].isin(fs)]
        if fe:
            vista = vista[vista["edad"].isin(fe)]
        if fp:
            vista = vista[vista["pelaje_predominante"].isin(fp)]
        if fl:
            vista = vista[vista["lugar"].str.contains(fl, case=False, na=False)]

        st.caption(f"Mostrando {len(vista)} de {len(df)} registros")
        st.dataframe(vista[list(C.ETIQUETAS)].rename(columns=C.ETIQUETAS), hide_index=True)

        if len(vista):
            st.divider()
            st.subheader("Ficha del gato")
            sel = st.selectbox("Selecciona un registro", vista["codigo"])
            fila = df[df["codigo"] == sel].iloc[0]
            fotos = db.fotos_de(int(fila["id"]))
            if fotos:
                cols = st.columns(len(fotos))
                for c, f in zip(cols, fotos):
                    c.image(f, width=260)
            for col, etiqueta in C.ETIQUETAS.items():
                if fila[col]:
                    st.markdown(f"**{etiqueta}:** {fila[col]}")

            with st.expander("🗑️ Eliminar este registro"):
                if pedir_clave("clave_del") and st.button("Eliminar definitivamente"):
                    db.eliminar(int(fila["id"]))
                    st.success("Registro eliminado.")
                    st.rerun()

# ------------------------------ 3. Estadísticas ------------------------------
with tab_stats:
    df = db.listar()
    tablas = stats.tablas(df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de gatos registrados", len(df))
    m2.metric("Hembras", int((df["sexo"] == "Hembra").sum()) if len(df) else 0)
    m3.metric("Hembras gestantes", int(((df["sexo"] == "Hembra") & (df["gestacion"] == "Sí")).sum()) if len(df) else 0)
    m4.metric("Lugares distintos", int(df["lugar"].str.strip().str.lower().nunique()) if len(df) else 0)

    if df.empty:
        st.info("Registra gatos para ver los gráficos.")
    else:
        items = list(tablas.items())
        for i in range(0, len(items), 2):
            cols = st.columns(2)
            for col, (titulo, t) in zip(cols, items[i : i + 2]):
                with col:
                    st.markdown(f"**{titulo}**")
                    if t["Cantidad"].sum() == 0:
                        st.caption("Sin datos todavía.")
                    else:
                        st.altair_chart(grafico(t))

# ------------------------------ 4. Excel y respaldo ------------------------------
with tab_export:
    st.subheader("📥 Descargar Excel")
    st.write("El libro incluye tres hojas: **Registros** (todos los datos ordenados), "
             "**Resumen** (tablas de conteo) y **Gráficos** (total y cantidades por cada sección).")
    con_fotos = st.checkbox("Incluir miniaturas de las fotos en la hoja Registros", value=True)
    if st.button("Generar Excel"):
        df = db.listar()
        if df.empty:
            st.warning("No hay registros para exportar.")
        else:
            with st.spinner("Generando archivo..."):
                st.session_state["excel"] = construir_excel(df, db.primeras_fotos() if con_fotos else None)
    if "excel" in st.session_state:
        st.download_button(
            "⬇️ Descargar registro_gatos.xlsx",
            st.session_state["excel"],
            file_name=f"registro_gatos_{datetime.now():%Y%m%d_%H%M}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.divider()
    st.subheader("💾 Copia de seguridad")
    st.warning(
        "En Streamlit Community Cloud los archivos del servidor **pueden borrarse** cuando la app se "
        "reinicia, se actualiza o queda inactiva. Descarga una copia de seguridad con frecuencia."
    )
    if os.path.exists(db.DB_PATH):
        st.download_button(
            "⬇️ Descargar copia de seguridad (.db)",
            db.respaldo_bytes(),
            file_name=f"respaldo_gatos_{datetime.now():%Y%m%d_%H%M}.db",
            mime="application/octet-stream",
        )
    with st.expander("♻️ Restaurar una copia de seguridad"):
        st.caption("Reemplaza TODOS los registros actuales por los de la copia.")
        archivo_db = st.file_uploader("Archivo .db", type=["db"], key="restore")
        if archivo_db and pedir_clave("clave_restore") and st.button("Restaurar"):
            try:
                db.restaurar(archivo_db.getvalue())
                st.success("Copia restaurada.")
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo restaurar: {e}")
