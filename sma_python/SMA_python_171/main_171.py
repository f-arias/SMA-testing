import os
from analysis_171 import SMA, get_default_sma_parameters, get_default_general_config

def main():
    """
    Función principal para demostrar el uso de la función SMA.
    """
    # --- Configuración de entrada y salida ---
    # Directorio de imágenes de prueba
    input_dir = "sma_python/GM_telemedLS_sample_A"
    # Directorio de salida para los resultados
    output_dir = "sma_python/output_171" # Directorio de salida específico

    # Asegurarse de que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)

    # --- Obtener configuraciones por defecto ---
    # El usuario puede ver qué parámetros se están utilizando
    default_params = get_default_sma_parameters()
    print("--- Parámetros de análisis por defecto ---")
    print(default_params)

    # Asignar el diccionario a una variable X como solicitó el usuario
    X = default_params
    print("\nDiccionario de parámetros asignado a la variable X.")

    default_config = get_default_general_config()
    print("\n--- Configuraciones generales por defecto ---")
    print(default_config)
    print("-" * 50)

    # --- Personalizar configuraciones (opcional) ---
    # Ejemplo de cómo un usuario podría modificar un parámetro
    custom_params = get_default_sma_parameters()
    custom_params["Osigma"] = "5" # Cambiar sigma para el análisis

    custom_config = get_default_general_config()
    custom_config["output_csv_name"] = "resultados_personalizados.csv"

    # --- Iterar sobre todas las imágenes del directorio ---
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
            input_image_path = os.path.join(input_dir, filename)

            print(f"\n--- Procesando la imagen: {filename} ---")

            # --- Llamada a la función SMA con configuraciones personalizadas ---
            results, output_mask = SMA(
                input_image_path=input_image_path,
                output_path=output_dir,
                analysis_params=custom_params,
                general_config=custom_config
            )

            # --- Resultados ---
            if results and output_mask is not None:
                print(f"Resultados del análisis para {filename}:")
                # Imprimir resultados de una forma más limpia
                for key, value in results.items():
                    if key != "image_name":
                        print(f"  - {key}: {value:.2f}")
            # La función SMA ya imprime un mensaje si el análisis falla
            print("-" * 50)

if __name__ == "__main__":
    main()
