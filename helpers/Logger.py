import tkinter as tk

class Logger:
    def __init__(self, window, root):
        '''
        Used to log information for user

        :param window: text area where information is printed
        :param root: application root
        '''
        self.window = window
        self.root = root

    def info(self, message: str):
        '''
        Prints message on text area and makes it visible

        :param message: message to log
        '''
        self.window.insert(tk.END, f'{message} \n')
        self.window.see(tk.END)
        self.root.update()

    def get(self) -> str:
        '''
        Returns all information that was logged till now
        '''
        return self.window.get("1.0", tk.END)

