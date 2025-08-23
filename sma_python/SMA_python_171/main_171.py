import os
from analysis_171 import SMA

def main():
    """
    Función principal para demostrar el uso de la función SMA, que ahora
    replica fielmente el flujo de trabajo del macro de Fiji.
    """
    # --- Configuración de entrada y salida ---
    # Directorio de imágenes de prueba
    input_dir = "sma_python/GM_telemedLS_sample_A"
    # Directorio de salida para los resultados
    output_dir = "sma_python/output_faithful"

    # Asegurarse de que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)

    # --- Parámetros de análisis (opcional) ---
    # Se puede pasar un diccionario vacío para usar todos los valores por defecto.
    # O se puede especificar solo los parámetros a cambiar.
    # Ejemplo: analysis_params = {"Tsigma": 8, "Osigma": "5"}
    analysis_params = {}

    print("Iniciando análisis con el pipeline fiel al macro de Fiji...")
    print(f"Directorio de entrada: {input_dir}")
    print(f"Directorio de salida: {output_dir}")
    print("-" * 50)

    # --- Iterar sobre todas las imágenes del directorio ---
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
