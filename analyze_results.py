import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_results(csv_path="Tsigma_test_results.csv"):
    """
    Analiza los resultados del test de Tsigma, genera una tabla y un gráfico
    para visualizar el rendimiento de la detección de aponeurosis.
    """
    # --- Carga y Preparación de Datos ---
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de resultados en '{csv_path}'.")
        print("Por favor, ejecute primero 'test_intensive_sma171.py'.")
        return

    # Convertir columnas booleanas a tipo numérico para poder calcular la media (tasa de éxito)
    df['upper_detected'] = df['upper_detected'].astype(int)
    df['lower_detected'] = df['lower_detected'].astype(int)
    df['both_detected'] = df['both_detected'].astype(int)

    # --- Análisis de Tasa de Éxito por Tsigma ---
    # Agrupar por valor de Tsigma y calcular la tasa de éxito para cada categoría
    results = df.groupby('tsigma').agg(
        total_images=('tsigma', 'size'),
        upper_success_rate=('upper_detected', 'mean'),
        lower_success_rate=('lower_detected', 'mean'),
        both_success_rate=('both_detected', 'mean')
    ).reset_index()

    # Convertir las tasas a porcentajes para una mejor visualización en la tabla
    results['upper_success_rate'] *= 100
    results['lower_success_rate'] *= 100
    results['both_success_rate'] *= 100

    # --- Presentación de Resultados en Tabla ---
    print("--- Análisis de Tasa de Éxito por Valor de Tsigma ---")
    # Formatear la tabla para que sea más legible
    results_table = results.copy()
    results_table['upper_success_rate'] = results_table['upper_success_rate'].map('{:.2f}%'.format)
    results_table['lower_success_rate'] = results_table['lower_success_rate'].map('{:.2f}%'.format)
    results_table['both_success_rate'] = results_table['both_success_rate'].map('{:.2f}%'.format)
    print(results_table.to_string(index=False))

    # --- Identificación del Mejor Tsigma ---
    best_tsigma_row = results.loc[results['both_success_rate'].idxmax()]
    best_tsigma_val = int(best_tsigma_row['tsigma'])
    best_rate = best_tsigma_row['both_success_rate']
    print(f"\nEl valor de Tsigma con mayor éxito en la detección de AMBAS aponeurosis es: {best_tsigma_val} (tasa de éxito: {best_rate:.2f}%)")

    # --- Generación del Gráfico ---
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(results['tsigma'], results['upper_success_rate'], marker='o', linestyle='-', label='Aponeurosis Superficial')
    ax.plot(results['tsigma'], results['lower_success_rate'], marker='s', linestyle='--', label='Aponeurosis Profunda')
    ax.plot(results['tsigma'], results['both_success_rate'], marker='^', linestyle='-', label='Ambas Aponeurosis (Éxito General)', color='green', linewidth=2.5)

    # Marcar el punto de máximo rendimiento
    ax.axvline(x=best_tsigma_val, color='red', linestyle='--', linewidth=1, label=f'Mejor Tsigma ({best_tsigma_val})')
    ax.plot(best_tsigma_val, best_rate, 'r*', markersize=15)

    # Títulos y etiquetas
    ax.set_title('Tasa de Éxito en la Detección de Aponeurosis vs. Tsigma', fontsize=16, fontweight='bold')
    ax.set_xlabel('Valor de Tsigma', fontsize=12)
    ax.set_ylabel('Tasa de Éxito (%)', fontsize=12)
    ax.set_xticks(results['tsigma'])
    ax.legend(frameon=True, shadow=True)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Añadir porcentajes en los puntos del gráfico de "Ambas Aponeurosis"
    for i, row in results.iterrows():
        ax.text(row['tsigma'], row['both_success_rate'] + 2, f"{row['both_success_rate']:.1f}%",
                ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.2'))


    plt.tight_layout()

    # Guardar el gráfico en un archivo
    output_image_path = "Tsigma_test_results.png"
    plt.savefig(output_image_path, dpi=300)
    print(f"\nGráfico de resultados guardado en: {output_image_path}")

if __name__ == "__main__":
    analyze_results()
