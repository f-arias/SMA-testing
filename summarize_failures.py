import pandas as pd

def summarize_failures(csv_path="Tsigma_test_results.csv"):
    """
    Analiza y resume las causas de fallo para el mejor valor de Tsigma, y
    ofrece una explicación cualitativa del impacto de este parámetro.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de resultados en '{csv_path}'.")
        print("Por favor, ejecute primero 'test_intensive_sma171.py'.")
        return

    # Encontrar el mejor Tsigma basado en la tasa de éxito de 'both_detected'
    # Asegurarse de que las columnas booleanas son numéricas para el cálculo
    df['both_detected'] = df['both_detected'].astype(int)
    best_tsigma = df.groupby('tsigma')['both_detected'].mean().idxmax()

    # Filtrar para el Tsigma de interés y los casos donde la detección de ambas aponeurosis falló
    failures_df = df[(df['tsigma'] == best_tsigma) & (df['both_detected'] == 0)]

    print(f"--- Análisis de Fallos para el Mejor Tsigma (Tsigma = {best_tsigma}) ---")

    if failures_df.empty:
        print("No se encontraron fallos para este valor de Tsigma. ¡Éxito del 100%!")
        return

    # Contar las razones de los fallos
    failure_counts = failures_df['failure_reason'].value_counts()

    total_images_at_best_tsigma = len(df[df['tsigma'] == best_tsigma])
    print(f"Se encontraron un total de {len(failures_df)} imágenes con fallos de un total de {total_images_at_best_tsigma}.")
    print("\nCausas de los fallos:")
    for reason, count in failure_counts.items():
        print(f"- {reason}: {count} ocurrencia(s)")

    # Analizar el impacto general de cada Tsigma
    print("\n--- Impacto General de Tsigma en los Fallos ---")
    print("A continuación se presenta un análisis cualitativo de por qué Tsigma afecta la detección:")
    print("\nTsigma BAJO (e.g., 1-2):")
    print("  - PRO: Es excelente para detectar aponeurosis finas y bien definidas.")
    print("  - CONTRA: Puede ser demasiado sensible al ruido o a texturas finas dentro del músculo,")
    print("    identificando incorrectamente estas como si fueran aponeurosis. Esto puede llevar a 'cruces' (ROI inválido).")

    print("\nTsigma MEDIO (e.g., 3-7):")
    print("  - PRO: Generalmente es un buen compromiso. Es menos sensible al ruido que un Tsigma bajo.")
    print("  - CONTRA: Si las aponeurosis en la imagen son más gruesas o más finas que el valor de sigma,")
    print("    el filtro 'tubeness' no las realzará lo suficiente, resultando en contornos rotos o no detectados.")

    print("\nTsigma ALTO (e.g., 8-12):")
    print("  - PRO: Es bueno para detectar aponeurosis muy gruesas o difusas.")
    print("  - CONTRA: Falla completamente con aponeurosis finas. El filtro busca estructuras tubulares anchas,")
    print("    por lo que las líneas delgadas se pierden. Esto a menudo resulta en 'Not enough long contours found'.")

    print("\n--- Conclusión sobre las Causas de Fallo ---")
    print("La causa principal de la NO-detección es la discordancia entre el valor de 'Tsigma' y el 'grosor' real de las aponeurosis en la imagen. No existe un único valor de Tsigma que funcione para todas las imágenes, ya que la apariencia de las aponeurosis varía según la calidad de la imagen, el equipo de ultrasonido y la anatomía del sujeto. El error 'Invalid ROI' es a menudo una consecuencia secundaria: si una aponeurosis se detecta incorrectamente (por ejemplo, una línea de ruido), puede cruzarse con la aponeurosis correcta, invalidando el análisis.")

if __name__ == "__main__":
    summarize_failures()
