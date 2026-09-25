"""
main.py - Punto de entrada
Algoritmos y Estructura de Datos III - TP Recursividad

Ejecución:
    python main.py
"""

import sys
import tkinter as tk
from gui import MazeGUI


def main():
    sys.setrecursionlimit(10000)  
    root = tk.Tk()
    MazeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
