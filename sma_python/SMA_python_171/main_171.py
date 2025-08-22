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

    # --- Ejecución 1: Flujo de trabajo por defecto (basado en FFT) ---
    print("\n" + "="*20 + " INICIANDO ANÁLISIS CON FILTRO FFT (POR DEFECTO) " + "="*20)

    config_fft = get_default_general_config()
    config_fft["output_csv_name"] = "resultados_fft.csv"

    params_fft = get_default_sma_parameters()

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
            input_image_path = os.path.join(input_dir, filename)
            print(f"\n--- Procesando (FFT): {filename} ---")
            SMA(
                input_image_path=input_image_path,
                output_path=output_dir,
                analysis_params=params_fft,
                general_config=config_fft
            )
            print("-" * 40)

    # --- Ejecución 2: Flujo de trabajo alternativo (con Tubeness) ---
    print("\n" + "="*20 + " INICIANDO ANÁLISIS CON FILTRO TUBENESS (SATO) " + "="*20)

    config_tubeness = get_default_general_config()
    config_tubeness["use_tubeness_filter"] = True
    config_tubeness["output_csv_name"] = "resultados_tubeness.csv"

    params_tubeness = get_default_sma_parameters()
    params_tubeness["Tsigma"] = 8 # Usar un valor de sigma para el filtro

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
            input_image_path = os.path.join(input_dir, filename)
            print(f"\n--- Procesando (Tubeness): {filename} ---")
            SMA(
                input_image_path=input_image_path,
                output_path=output_dir,
                analysis_params=params_tubeness,
                general_config=config_tubeness
            )
            print("-" * 40)

if __name__ == "__main__":
    main()
