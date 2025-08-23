import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Add the sma_python directory to the python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sma_python.SMA_python_171.analysis_171 import SMA

def run_tsigma_sweep_test():
    """
    Runs an intensive test of the SMA171 function, sweeping the Tsigma
    parameter to find the optimal value for aponeurosis detection.

    Returns:
        dict: A dictionary containing the success counts for each Tsigma value.
    """
    print("Starting SMA171 Tsigma sweep test...")

    # --- Configuration ---
    image_dir = "sma_python/GM_telemedLS_sample_A"
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    tsigma_range = range(1, 13)
    results_by_tsigma = {tsigma: 0 for tsigma in tsigma_range}

    # --- Test Execution ---
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp'))]
    total_images = len(image_files)

    print(f"Found {total_images} images to analyze in '{image_dir}'")
    print(f"Sweeping Tsigma from {tsigma_range.start} to {tsigma_range.stop - 1}")

    for tsigma in tsigma_range:
        # This print will be suppressed, which is fine
        print(f"\n--- Testing with Tsigma = {tsigma} ---")
        success_count = 0

        for image_file in image_files:
            image_path = os.path.join(image_dir, image_file)

            analysis_params = {"Tsigma": tsigma}

            results, mask = SMA(
                input_image_path=image_path,
                output_path=output_dir,
                analysis_params=analysis_params,
                csv_output=False
            )

            if results is not None and mask is not None:
                success_count += 1

        results_by_tsigma[tsigma] = success_count

    return results_by_tsigma


if __name__ == "__main__":
    # Suppress console output from the SMA function to keep the summary clean
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

    results_summary = {}
    try:
        results_summary = run_tsigma_sweep_test()
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout

    # --- Now, print the summary with stdout restored ---
    total_images = len(os.listdir("sma_python/GM_telemedLS_sample_A"))
    print("\n--- Tsigma Sweep Test Summary ---")
    if not results_summary:
        print("The test did not produce a summary.")
    else:
        for tsigma, successes in results_summary.items():
            print(f"Tsigma = {tsigma:2d}: {successes:2d}/{total_images} successful detections")

        # Find and print the best Tsigma
        best_tsigma = max(results_summary, key=results_summary.get)
        print(f"\nOptimal Tsigma value: {best_tsigma} with {results_summary[best_tsigma]} successes.")

        # --- Plotting Results ---
        tsigmas = list(results_summary.keys())
        successes = list(results_summary.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(tsigmas, successes, color='skyblue')

        ax.set_xlabel('Tsigma Value')
        ax.set_ylabel('Number of Successful Detections')
        ax.set_title('Effect of Tsigma on Aponeurosis Detection Success')
        ax.set_xticks(tsigmas)
        ax.bar_label(bars)

        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.savefig('Tsigma_test_results.png')
        print("\nResults chart saved to 'Tsigma_test_results.png'")
