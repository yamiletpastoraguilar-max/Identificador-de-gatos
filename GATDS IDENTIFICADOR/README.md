# 🐱 Registro de Gatos

Gestor de información en **Streamlit** para registrar gatos a partir de fotos, completar sus datos y
exportar todo a **Excel** con tablas y gráficos.

## Datos que se registran
Fotos (hasta 3, subidas o tomadas con la cámara) · lugar donde se vio · color de pelaje predominante
(negro, blanco, gris, anaranjado, crema, marrón o combinación a especificar) · sexo aparente
(hembra, macho, no determinado) · gestación (si es hembra) · estado sanitario visible ·
edad aparente (cría, joven, adulto, adulto mayor, indeterminado) · condición corporal
(muy delgado, delgado, adecuado, sobrepeso, obeso, otro) · tamaño aproximado
(~10 cm cría, ~25 cm joven, ~45 cm adulto) · información adicional libre.

## Excel generado
- **Registros**: todos los datos ordenados (con filtros, panel fijo y miniatura de la foto).
- **Resumen**: total y tablas de conteo por cada sección (más lugares y registros por fecha).
- **Gráficos**: total de gatos y un gráfico por cada sección (gráficos nativos de Excel).

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud
1. Sube la carpeta a un repositorio de GitHub:
   ```bash
   git init && git add . && git commit -m "Registro de gatos"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/registro-gatos.git
   git push -u origin main
   ```
2. En https://share.streamlit.io → **Create app** → elige el repositorio, rama `main`, archivo `app.py` → **Deploy**.
3. (Opcional) En **Settings → Secrets** agrega `ADMIN_PASSWORD = "tu-clave"` para proteger la eliminación
   de registros y la restauración de copias.

## ⚠️ Importante: persistencia de datos
Los datos se guardan en un archivo SQLite (`data/gatos.db`). En Streamlit Community Cloud el disco del
servidor **no es permanente**: puede borrarse al reiniciar o actualizar la app. Usa la pestaña
**Excel y respaldo** para descargar el Excel y la copia de seguridad (.db) con frecuencia, y restaurarla cuando haga falta.
Si necesitas almacenamiento permanente, se puede conectar a Supabase o Google Sheets.
