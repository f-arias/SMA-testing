import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Añade el directorio de sma_python al path de Python para permitir la importación
# de módulos desde una ubicación diferente.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sma_python.SMA_python_171.analysis_171 import SMA

# --- Constantes de Configuración ---
IMAGE_DIR = "sma_python/GM_telemedLS_sample_A"
OUTPUT_DIR = "test_output"
IMAGE_FILES = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp'))]
TOTAL_IMAGES = len(IMAGE_FILES)
CAPTION_TEXT = f"Configuración: Por defecto. Imágenes: {TOTAL_IMAGES} de la muestra '{IMAGE_DIR}'"
TSIGMA_CAPTION_TEXT = f"Configuración: Barrido de Tsigma. Imágenes: {TOTAL_IMAGES} de la muestra '{IMAGE_DIR}'"

def run_simple_test():
    """
    Realiza un testeo intensivo simple usando los parámetros por defecto
    de la función SMA171 y genera un gráfico de éxito/fracaso.
    """
    print("--- Iniciando Testeo Simple con Parámetros por Defecto ---")

    success_count = 0
    # Itera sobre cada imagen y la procesa con la configuración por defecto.
    for image_file in IMAGE_FILES:
        image_path = os.path.join(IMAGE_DIR, image_file)
        # Llama a la función de análisis. El diccionario de parámetros está vacío
        # para asegurar que se usen los valores por defecto definidos en SMA().
        results, mask = SMA(
            input_image_path=image_path,
            output_path=OUTPUT_DIR,
            analysis_params={},
            csv_output=False
        )
        if results is not None and mask is not None:
            success_count += 1

    failure_count = TOTAL_IMAGES - success_count
    print(f"Resultados: {success_count} éxitos, {failure_count} fracasos.")

    # --- Generación del Gráfico ---
    labels = ['Éxito', 'Fracaso']
    counts = [success_count, failure_count]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, counts, color=['green', 'red'])
    ax.set_ylabel('Número de Imágenes')
    ax.set_title('Resultados del Testeo SMA171 con Parámetros por Defecto')
    ax.bar_label(bars)

    # Añade la leyenda solicitada en la parte inferior del gráfico.
    plt.figtext(0.5, 0.01, CAPTION_TEXT, ha="center", fontsize=8, style='italic')
    plt.tight_layout(rect=[0, 0.05, 1, 1]) # Ajusta el layout para dar espacio a la leyenda

    plt.savefig('test_results.png')
    print("Gráfico de resultados guardado en 'test_results.png'\n")

def run_tsigma_sweep_test():
    """
    Realiza un testeo intensivo variando el parámetro Tsigma para encontrar
    el valor óptimo para la detección de aponeurosis.
    """
    print("--- Iniciando Testeo con Barrido de Parámetro Tsigma ---")

    tsigma_range = range(1, 13)
    # Diccionario para almacenar los resultados: {tsigma: num_exitos}
    results_by_tsigma = {tsigma: 0 for tsigma in tsigma_range}

    print(f"Analizando {TOTAL_IMAGES} imágenes con Tsigma de {tsigma_range.start} a {tsigma_range.stop - 1}...")

    # Bucle anidado: recorre cada Tsigma y, para cada uno, todas las imágenes.
    for tsigma in tsigma_range:
        success_count = 0
        for image_file in IMAGE_FILES:
            image_path = os.path.join(IMAGE_DIR, image_file)
            analysis_params = {"Tsigma": tsigma}
            results, mask = SMA(
                input_image_path=image_path,
                output_path=OUTPUT_DIR,
                analysis_params=analysis_params,
                csv_output=False
            )
            if results is not None and mask is not None:
                success_count += 1
        results_by_tsigma[tsigma] = success_count

    # --- Impresión de Resultados en Consola ---
    print("\n--- Resumen del Test de Barrido de Tsigma ---")
    for tsigma, successes in results_by_tsigma.items():
        print(f"Tsigma = {tsigma:2d}: {successes:2d}/{TOTAL_IMAGES} detecciones exitosas")

    best_tsigma = max(results_by_tsigma, key=results_by_tsigma.get)
    print(f"\nValor óptimo de Tsigma: {best_tsigma} con {results_by_tsigma[best_tsigma]} éxitos.")

    # --- Generación del Gráfico ---
    tsigmas = list(results_by_tsigma.keys())
    successes = list(results_by_tsigma.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(tsigmas, successes, color='skyblue')

    ax.set_xlabel('Valor de Tsigma')
    ax.set_ylabel('Número de Detecciones Exitosas')
    ax.set_title('Efecto de Tsigma en el Éxito de Detección de Aponeurosis')
    ax.set_xticks(tsigmas)
    ax.bar_label(bars)

    # Añade la leyenda solicitada.
    plt.figtext(0.5, 0.01, TSIGMA_CAPTION_TEXT, ha="center", fontsize=8, style='italic')
    plt.tight_layout(rect=[0, 0.05, 1, 1])

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.savefig('Tsigma_test_results.png')
    print("Gráfico de resultados guardado en 'Tsigma_test_results.png'\n")


if __name__ == "__main__":
    # Crea el directorio de salida si no existe.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Bloque para suprimir la salida detallada de la función SMA y mantener
    # el resumen del test limpio.
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

    try:
        # Ejecuta ambas funciones de testeo.
        run_simple_test()
        run_tsigma_sweep_test()
    finally:
        # Restaura la salida estándar para poder ver los prints finales.
        sys.stdout.close()
        sys.stdout = original_stdout
        print("--- Todos los testeos han finalizado. ---")
        print("Los resultados y gráficos han sido generados.")
