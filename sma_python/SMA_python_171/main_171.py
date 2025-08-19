import tkinter as tk
from sma_gui_171 import SMAGUI171
import analysis_171 as analysis
import os
import csv
import cv2

class App171:
    def __init__(self, root):
        self.results_list = []
        self.root = root
        self.app_gui = SMAGUI171(root)
        self.app_gui.set_run_analysis_callback(self.start_analysis)

    def start_analysis(self, params):
        analysis_type = params["analysis"]
        output_dir = params.get("outputDir")

        if analysis_type == "Image":
            image_path = params.get("inputFile")
            if not image_path or not os.path.exists(image_path):
                print("Error: El archivo de entrada no es válido.")
                return

            if not output_dir:
                output_dir = os.path.dirname(image_path)
            os.makedirs(output_dir, exist_ok=True)

            self.process_and_save(image_path, params, output_dir)

        elif analysis_type == "Folder":
            input_dir = params.get("inputDir")
            if not input_dir or not os.path.isdir(input_dir):
                print("Error: El directorio de entrada no es válido.")
                return
            if not output_dir:
                print("Error: El directorio de salida no está especificado.")
                return
            os.makedirs(output_dir, exist_ok=True)

            extension = params.get("extension", ".tif")
            for filename in os.listdir(input_dir):
                if filename.endswith(extension):
                    image_path = os.path.join(input_dir, filename)
                    print(f"--- Procesando archivo: {filename} ---")
                    self.process_and_save(image_path, params, output_dir)

        self.save_csv_results(output_dir)
        if self.root:
            self.root.quit()

    def process_and_save(self, image_path, params, output_dir):
        results, output_mask = analysis.process_single_image_171(image_path, params)
        if results and output_mask is not None:
            results["image_name"] = os.path.basename(image_path)
            self.results_list.append(results)

            filename, _ = os.path.splitext(os.path.basename(image_path))
            output_path = os.path.join(output_dir, f"processed_mask_{filename}.png")
            cv2.imwrite(output_path, output_mask)
            print(f"Máscara procesada guardada en: {output_path}")

    def save_csv_results(self, output_dir):
        if not self.results_list:
            print("No se generaron resultados para guardar.")
            return

        output_path = os.path.join(output_dir, "resultados_171.csv")
        print(f"Guardando resultados en: {output_path}")

        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = self.results_list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results_list)

        print("Resultados guardados exitosamente.")

def main():
    root = tk.Tk()
    app = App171(root)
    root.mainloop()

if __name__ == "__main__":
    main()
