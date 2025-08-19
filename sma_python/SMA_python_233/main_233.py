import tkinter as tk
from sma_gui_233 import SMAGUI
import analysis_233 as analysis
import os
import matplotlib
matplotlib.use('Agg')
import csv
import cv2

class App:
    def __init__(self, root):
        self.results_list = []
        self.root = root
        self.app_gui = SMAGUI(root)
        self.app_gui.set_run_analysis_callback(self.start_analysis)

    def start_analysis(self, params):
        output_dir = params.get("outputDir")
        if not output_dir:
            if params["analysis"] == "Open folder":
                output_dir = params["inputDir"]
            else:
                output_dir = os.path.dirname(params["inputFile"])

        os.makedirs(output_dir, exist_ok=True)

        if params["analysis"] == "Open file":
            if not params["inputFile"] or not os.path.exists(params["inputFile"]):
                print("Error: El archivo de entrada no es válido.")
                return

            results, vis_img = analysis.process_single_image(params["inputFile"], params)
            if results and vis_img is not None:
                results["image_name"] = os.path.basename(params["inputFile"])
                self.results_list.append(results)

                output_image_path = os.path.join(output_dir, "processed_" + os.path.basename(params["inputFile"]))
                cv2.imwrite(output_image_path, vis_img)
                print(f"Imagen procesada guardada en: {output_image_path}")

        elif params["analysis"] == "Open folder":
            input_dir = params["inputDir"]
            if not input_dir or not os.path.isdir(input_dir):
                print("Error: El directorio de entrada no es válido.")
                return

            extension = params.get("extension", ".tif")
            for filename in os.listdir(input_dir):
                if filename.endswith(extension):
                    image_path = os.path.join(input_dir, filename)
                    print(f"--- Procesando archivo: {filename} ---")
                    results, vis_img = analysis.process_single_image(image_path, params)
                    if results and vis_img is not None:
                        results["image_name"] = filename
                        self.results_list.append(results)

                        output_image_path = os.path.join(output_dir, "processed_" + filename)
                        cv2.imwrite(output_image_path, vis_img)
                        print(f"Imagen procesada guardada en: {output_image_path}")

        self.save_results(output_dir)
        if self.root:
            self.root.quit()

    def save_results(self, output_dir):
        if not self.results_list:
            print("No se generaron resultados para guardar.")
            return

        output_path = os.path.join(output_dir, "resultados.csv")
        print(f"Guardando resultados en: {output_path}")

        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = self.results_list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results_list)

        print("Resultados guardados exitosamente.")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
