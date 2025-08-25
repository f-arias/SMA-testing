import os
import csv
from sma_python.SMA_python_171.analysis_171 import SMA
import time

def run_intensive_test():
    """
    Corre una prueba intensiva de la función SMA 171, variando el parámetro Tsigma
    y registrando el éxito en la detección de aponeurosis para un conjunto de imágenes.
    """
    # --- Configuración del Test ---
    # Directorios que contienen las imágenes de ultrasonido a analizar.
    image_directories = [
        "sma_python/GM_telemedLS_sample_A",
        "sma_python/GM_philips_sample_B"
    ]

    # Rango de valores de Tsigma a probar.
    tsigma_range = range(1, 13)

    # Archivo CSV para guardar los resultados detallados del test.
    output_csv_path = "Tsigma_test_results.csv"

    # --- Inicialización de Resultados ---
    # Encabezados para el archivo CSV.
    fieldnames = ["image_path", "tsigma", "upper_detected", "lower_detected", "both_detected", "failure_reason"]

    # Eliminar el archivo de resultados anterior si existe.
    if os.path.exists(output_csv_path):
        os.remove(output_csv_path)

    # Escribir los encabezados en el nuevo archivo CSV.
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    print("--- Iniciando Test Intensivo de SMA 171 ---")
    start_time = time.time()

    # --- Bucle Principal de Pruebas ---
    for tsigma_value in tsigma_range:
        print(f"\n--- Probando con Tsigma = {tsigma_value} ---")

        for directory in image_directories:
            if not os.path.isdir(directory):
                print(f"Directorio no encontrado, saltando: {directory}")
                continue

            for filename in os.listdir(directory):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
                    image_path = os.path.join(directory, filename)
                    print(f"Procesando: {os.path.basename(image_path)}")

                    # --- Llamada a la Función de Análisis ---
                    # Define los parámetros de análisis para esta ejecución.
                    analysis_params = {"Tsigma": tsigma_value}

                    # Directorio de salida para las máscaras (opcional, para depuración).
                    # Se deshabilita para no generar demasiados archivos.
                    output_dir = "sma_python/output_temp"

                    # Llama a la función SMA y obtiene los resultados.
                    # La función SMA debe ser modificada para devolver 'detection_status'.
                    _, _, detection_status = SMA(
                        input_image_path=image_path,
                        output_path=output_dir,
                        analysis_params=analysis_params,
                        csv_output=False  # Deshabilitamos el CSV de la función original.
                    )

                    # --- Registro de Resultados ---
                    # Prepara la fila de datos para el CSV.
                    result_row = {
                        "image_path": image_path,
                        "tsigma": tsigma_value,
                        "upper_detected": detection_status.get("upper_found", False),
                        "lower_detected": detection_status.get("lower_found", False),
                        "both_detected": detection_status.get("both_found", False),
                        "failure_reason": detection_status.get("failure_reason", "")
                    }

                    # Añade la fila al archivo CSV.
                    with open(output_csv_path, 'a', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(result_row)

    end_time = time.time()
    print(f"\n--- Test completado en {end_time - start_time:.2f} segundos ---")
    print(f"Resultados guardados en: {output_csv_path}")

if __name__ == "__main__":
    run_intensive_test()
