import os
from analysis_171 import SMA

def main():
    """
    Función principal para demostrar el uso de la función SMA.
    """
    # --- Configuración de entrada y salida ---
    # Directorio de imágenes de prueba
    input_dir = "sma_python/GM_telemedLS_sample_A"
    # Directorio de salida para los resultados
    output_dir = "sma_python/output"

    # Asegurarse de que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)

    # --- Parámetros de análisis (opcional) ---
    # Si no se proporcionan, se usarán los valores por defecto de la función SMA.
    analysis_params = {
        "cropping": "Automatic",
        "Osigma": "4"
    }

    # --- Iterar sobre todas las imágenes del directorio ---
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
            input_image_path = os.path.join(input_dir, filename)

            # --- Llamada a la función SMA ---
            print(f"--- Procesando la imagen: {input_image_path} ---")

            results, output_mask = SMA(
                input_image_path=input_image_path,
                output_path=output_dir,
                analysis_params=analysis_params,
                csv_output=True
            )

            # --- Resultados ---
            if results and output_mask is not None:
                print(f"--- Análisis de {filename} completado exitosamente ---")
                print("Resultados del análisis:")
                for key, value in results.items():
                    print(f"  {key}: {value}")
            else:
                print(f"--- El análisis de {filename} no pudo completarse ---")
            print("-" * 50)

if __name__ == "__main__":
    main()
