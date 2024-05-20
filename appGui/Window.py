import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext

import apiConection.PDFDownload as PDFDownload
from fileHandling.FileHandler import FileHandler
from helpers.Logger import Logger
from apiConection.NIPValidation import NipCheck


class Window():
    def __init__(self):
        '''
        Window application
        '''
        self.counter = 0

        def choose_input_file():
            file_path = filedialog.askopenfilename(initialdir="~/Desktop", title="Select CSV file",
                                                   filetypes=(
                                                   ("CSV files", "*.csv"), ("All files", "*.*")))
            if file_path:
                input_file_entry.delete(0, tk.END)
                input_file_entry.insert(0, file_path)

        def choose_output_folder():
            folder_path = filedialog.askdirectory(title="Select output folder",
                                                  initialdir="~/Desktop")
            if folder_path:
                output_folder_entry.delete(0, tk.END)
                output_folder_entry.insert(0, folder_path)

        def check_with_screenshot(self, logger: Logger):
            fileHandler = FileHandler(output_folder_entry.get(), input_file_entry.get(), logger)
            nipCheck = NipCheck(fileHandler, logger)
            nipCheck.checkStatus()
            validNips = nipCheck.validateNips()

            if screenshot_var.get() == 1:
                logger.info('Create Screenshot Directory')
                fileHandler.createScreenshotsDir()

                logger.info('Making Screenshots')
                validNipsLen = len(validNips)

                if validNipsLen > 0:
                    PDFDownload.downloadPdfForNips(validNips, logger, fileHandler)
                else:
                    logger.info('No valid nips to make screenshots for.')
            else:
                print('Done')

            fileHandler.dumpLoggerFile()

            logger.info('Program ended')
            self.counter = 0


        # Create main window
        self.root = tk.Tk()
        self.root.title("Nip UE Validator")

        # Input file selection
        input_file_label = tk.Label(self.root, text="Input CSV File:")
        input_file_label.grid(row=0, column=0, padx=5, pady=5)
        input_file_entry = tk.Entry(self.root, width=50)
        input_file_entry.grid(row=0, column=1, padx=5, pady=5)
        choose_input_button = tk.Button(self.root, text="Browse", command=choose_input_file)
        choose_input_button.grid(row=0, column=2, padx=5, pady=5)

        # Output folder selection
        output_folder_label = tk.Label(self.root, text="Output Folder:")
        output_folder_label.grid(row=1, column=0, padx=5, pady=5)
        output_folder_entry = tk.Entry(self.root, width=50)
        output_folder_entry.grid(row=1, column=1, padx=5, pady=5)
        choose_output_button = tk.Button(self.root, text="Browse", command=choose_output_folder)
        choose_output_button.grid(row=1, column=2, padx=5, pady=5)

        # Checkbox for screenshot
        screenshot_var = tk.IntVar()
        screenshot_checkbox = tk.Checkbutton(self.root, text="Build with screenshot",
                                             variable=screenshot_var)
        screenshot_checkbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        screenshot_var.set(1)  # Default checked

        # Check button
        check_button = tk.Button(self.root, text="Check", command=lambda :
        check_with_screenshot(self, logger))
        check_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        text_field_label = tk.Label(self.root, text="Program Text:")
        text_field_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)
        self.text_field = scrolledtext.ScrolledText(self.root, width=50, height=10, wrap=tk.WORD)
        self.text_field.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        logger = Logger(self.text_field, self.root)

        self.root.mainloop()
