import os

DIRECTORIO_DEL_PROYECTO = "."

NOMBRE_ARCHIVO_SALIDA = "codigo_explicado.txt"

# --- COMPLETA AQUÍ ---
# Solo se incluirán los archivos que terminen con estas extensiones.
EXTENSIONES_A_INCLUIR = [
    ".py",
    ".html",
    ".css",
    ".js",
    ".yml",
    ".md",
    ".txt",
    ".yaml",
    "Dockerfile"
]

CARPETAS_A_IGNORAR = [
    "node_modules",
    "venv",
    "__pycache__",
    ".git",
    ".vscode",
]


print(f"Iniciando la extracción de archivos tipo {', '.join(EXTENSIONES_A_INCLUIR)}")
print(f"Directorio analizado: '{DIRECTORIO_DEL_PROYECTO}'")

with open(NOMBRE_ARCHIVO_SALIDA, "w", encoding="utf-8") as archivo_final:

    for ruta_actual, lista_subcarpetas, lista_archivos in os.walk(DIRECTORIO_DEL_PROYECTO):

        lista_subcarpetas[:] = [
            carpeta for carpeta in lista_subcarpetas
            if carpeta not in CARPETAS_A_IGNORAR
        ]

        for nombre_archivo in lista_archivos:

            if not any(nombre_archivo.endswith(ext) for ext in EXTENSIONES_A_INCLUIR):
                continue

            # --- CAMBIO REALIZADO AQUÍ ---
            # Ahora el encabezado es mucho más descriptivo.
            encabezado = f"// En la ruta '{ruta_actual}' está el archivo con nombre '{nombre_archivo}'\n"
            archivo_final.write("\n" + "="*80 + "\n") # Línea separadora para mayor claridad
            archivo_final.write(encabezado)
            archivo_final.write("="*80 + "\n\n")

            ruta_completa_del_archivo = os.path.join(ruta_actual, nombre_archivo)

            try:
                with open(ruta_completa_del_archivo, "r", encoding="utf-8", errors="ignore") as archivo_a_leer:
                    contenido = archivo_a_leer.read()
                    archivo_final.write(contenido)
                print(f"  -> Incluyendo: {ruta_completa_del_archivo}")

            except Exception as error:
                archivo_final.write(f"[ERROR: No se pudo leer este archivo. Razón: {error}]\n")
                print(f"  -> ERROR al leer: {ruta_completa_del_archivo}")


print(f"\n¡Proceso terminado! :D")
print(f"El código con las rutas explicadas se ha guardado en: '{NOMBRE_ARCHIVO_SALIDA}'")