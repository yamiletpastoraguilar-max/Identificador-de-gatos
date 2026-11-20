"""Opciones de los formularios y etiquetas de columnas."""

PELAJES = ["Negro", "Blanco", "Gris", "Anaranjado", "Crema", "Marrón", "Combinación de colores"]
SEXOS = ["Hembra", "Macho", "No determinado"]
GESTACION = ["Sí", "No", "No determinado"]
EDADES = ["Cría", "Joven", "Adulto", "Adulto mayor", "Indeterminado"]
CONDICIONES = ["Muy delgado", "Delgado", "Adecuado", "Sobrepeso", "Obeso", "Otro"]
TAMANOS = ["Cría (~10 cm)", "Joven (~25 cm)", "Adulto (~45 cm)"]
SANITARIO = [
    "Aparentemente sano",
    "Heridas visibles",
    "Pelaje en mal estado / zonas sin pelo",
    "Secreción en ojos o nariz",
    "Parásitos externos (pulgas/garrapatas)",
    "Lesiones en la piel",
    "Cojera o dificultad para caminar",
    "Otro",
]

# Columna en base de datos -> encabezado visible (en el orden de la hoja de Excel)
ETIQUETAS = {
    "codigo": "Código",
    "fecha": "Fecha de registro",
    "registrado_por": "Registrado por",
    "lugar": "Lugar donde se vio",
    "pelaje_predominante": "Color de pelaje predominante",
    "pelaje_detalle": "Detalle de la combinación de colores",
    "sexo": "Sexo aparente",
    "gestacion": "Gestación (solo hembras)",
    "estado_sanitario": "Estado sanitario visible",
    "estado_sanitario_detalle": "Detalle del estado sanitario",
    "edad": "Edad aparente",
    "condicion_corporal": "Condición corporal",
    "condicion_detalle": "Detalle de la condición corporal",
    "tamano": "Tamaño aproximado",
    "info_adicional": "Información adicional",
}
