import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pytesseract
import pandas as pd
from logic import (
    calcular_ritmo_estilo, calcular_forma_score, calcular_probabilidad_implicita,
    calcular_valor_esperado, calcular_sensibilidad, evaluar_tendencia_publica,
    evaluar_variables_externas, detectar_ilusiones_mercado, ensamblar_modelo_completo
)

class BettingAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Betting Data Analyzer")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Create upload button
        self.upload_btn = tk.Button(
            self.main_frame,
            text="Upload Image",
            command=self.upload_image
        )
        self.upload_btn.pack(pady=10)
        
        # Create image display area
        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(pady=10)
        
        # Create analyze button
        self.analyze_btn = tk.Button(
            self.main_frame,
            text="Analyze Image",
            command=self.analyze_image,
            state=tk.DISABLED
        )
        self.analyze_btn.pack(pady=10)
        
        # Create results area
        self.results_text = tk.Text(self.main_frame, height=20, width=80)
        self.results_text.pack(pady=10)
        
        self.current_image = None
        self.ocr_text = None

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            # Load and display image
            image = Image.open(file_path)
            image.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.current_image = file_path
            self.analyze_btn.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Image uploaded successfully!\nClick 'Analyze Image' to process.")

    def analyze_image(self):
        if not self.current_image:
            messagebox.showerror("Error", "Please upload an image first!")
            return

        try:
            # Perform OCR
            self.ocr_text = pytesseract.image_to_string(Image.open(self.current_image))
            
            # Process the OCR text and run betting logic
            # TODO: Add OCR text processing logic here
            
            # For now, just display the OCR text
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "OCR Results:\n\n")
            self.results_text.insert(tk.END, self.ocr_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BettingAnalyzerApp(root)
    root.mainloop() 