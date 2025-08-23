import os
from analysis_171 import SMA

def main():
    """
    Función principal para demostrar el uso de la función SMA, que ahora
    replica fielmente el flujo de trabajo del macro de Fiji.
    """
    # --- Configuración de Rutas de Entrada y Salida ---
    # Define el directorio donde se encuentran las imágenes a analizar.
    input_dir = "sma_python/GM_telemedLS_sample_A"
    # Define el directorio donde se guardarán los resultados (imágenes procesadas y CSV).
    output_dir = "sma_python/output_faithful"

    # Crea el directorio de salida si no existe para evitar errores.
    os.makedirs(output_dir, exist_ok=True)

    # --- Configuración de Parámetros de Análisis ---
    # Para este script de demostración, se utilizan los parámetros por defecto.
    # Para anular un parámetro, se pasaría un diccionario, por ejemplo:
    # analysis_params = {"Tsigma": 8}
    analysis_params = {}

    print("Iniciando análisis con el pipeline fiel al macro de Fiji...")
    print(f"Directorio de entrada: {input_dir}")
    print(f"Directorio de salida: {output_dir}")
    print("-" * 50)

    # --- Bucle Principal de Procesamiento ---
    # Itera sobre cada archivo en el directorio de entrada.
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
            input_image_path = os.path.join(input_dir, filename)

            print(f"\n--- Procesando la imagen: {filename} ---")

            # --- Llamada a la función SMA ---
            results, output_mask = SMA(
                input_image_path=input_image_path,
                output_path=output_dir,
                analysis_params=analysis_params
            )

            # --- Resultados ---
            if results:
                print("Resultados del análisis:")
                for key, value in sorted(results.items()):
                    if key != "image_name":
                        try:
                            print(f"  - {key}: {value:.2f}")
                        except (TypeError, ValueError):
                            print(f"  - {key}: {value}")
            # La función SMA ya imprime un mensaje si el análisis falla.
            print("-" * 50)

if __name__ == "__main__":
    main()
