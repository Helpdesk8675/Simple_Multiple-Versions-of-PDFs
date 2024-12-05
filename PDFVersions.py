import tkinter as tk
from tkinter import filedialog, ttk
from os import getcwd, scandir, path, mkdir, chdir, listdir
import datetime
import mmap
import re

class PDFRecoveryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Version Recovery Tool")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input folder selection
        ttk.Label(main_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output folder selection
        ttk.Label(main_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=3)
        
        # Process button
        ttk.Button(main_frame, text="Process PDFs", command=self.process_pdfs).grid(row=4, column=0, columnspan=3, pady=10)
        
        # Add padding to all elements
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
    
    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)
    
    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)
    
    def process_pdfs(self):
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        
        if not input_dir or not output_dir:
            self.status_var.set("Please select both input and output folders")
            return
        
        self.status_var.set("Processing...")
        self.root.update()
        
        try:
            # Create output directory with timestamp
            timestamp_dir = path.join(output_dir, "Output - " + str(datetime.datetime.now()).replace(":",""))
            mkdir(timestamp_dir)
            chdir(timestamp_dir)
            
            # Get list of PDF files
            pdf_files = [f for f in listdir(input_dir) if f.lower().endswith('.pdf')]
            self.progress['maximum'] = len(pdf_files)
            
            for i, pdf_file in enumerate(pdf_files):
                self.status_var.set(f"Processing {pdf_file}")
                self.progress['value'] = i + 1
                self.root.update()
                
                with open(path.join(input_dir, pdf_file), "rb+") as f:
                    data = mmap.mmap(f.fileno(), 0)
                    mo = list(re.finditer(b'EOF', data))
                    version = 0
                    tempX = None
                    
                    if len(mo) > 2:
                        pdf_dir = path.join(timestamp_dir, pdf_file)
                        if not path.exists(pdf_dir):
                            mkdir(pdf_dir)
                        
                        for x in mo:
                            if version > 1:
                                output_name = path.join(pdf_dir, f"Recovered Version {version}.pdf")
                                with open(output_name, 'w+b') as newFile:
                                    data.seek(0)
                                    newFile.write(data.read(tempX.end()))
                                data.seek(0)
                            elif version == 1:
                                tempX = x
                            version += 1
                    
                    data.close()
            
            self.status_var.set("Processing complete!")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFRecoveryGUI(root)
    root.mainloop()
