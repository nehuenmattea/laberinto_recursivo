import tkinter as tk
from tkinter import ttk
from laberinto import Laberinto, PARED, LIBRE, INICIO, SALIDA1, SALIDA2

TAM_CELDA = 24
RETARDO_MS = 10         # Milisegundos por paso en la fase de exploración
RETARDO_OPTIMO_MS = 18  # Milisegundos por paso en el recorrido óptimo

# Paleta de colores 
COLOR_PARED = "#1e293b"       # Azul pizarra oscuro
COLOR_LIBRE = "#f8fafc"       # Blanco suave
COLOR_INICIO = "#10b981"      # Esmeralda
COLOR_SALIDA1 = "#ef4444"     # Rojo carmesí
COLOR_SALIDA2 = "#f97316"     # Naranja ámbar
COLOR_AVANCE = "#38bdf8"      # Celeste claro (avance en exploración)
COLOR_RETROCESO = "#fed7aa"   # Melocotón / naranja suave (retroceso en exploración)
COLOR_RUTA = "#22c55e"        # Verde brillante (trayecto óptimo)
COLOR_JUGADOR = "#8b5cf6"     # Púrpura

TECLAS = {
    "Up": (-1, 0), "w": (-1, 0), "W": (-1, 0),
    "Down": (1, 0), "s": (1, 0), "S": (1, 0),
    "Left": (0, -1), "a": (0, -1), "A": (0, -1),
    "Right": (0, 1), "d": (0, 1), "D": (0, 1),
}

DIRECCIONES = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Arriba, Derecha, Abajo, Izquierda


class MazeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Laberinto - Backtracking Recursivo Exhaustivo")
        self.root.resizable(False, False)

        self.lab = Laberinto()
        self.jugador = self.lab.inicio
        self.pasos_manuales = 0
        self.animando = False
        self._cancelar_animacion = False
        self._despues_id = None

        # Datos de la última resolución automática
        self.ultima_resolucion = None

        # ---------- Barra de Controles Superior ----------
        barra = tk.Frame(root, bg="#f1f5f9", padx=10, pady=8)
        barra.pack(fill="x")

        self.btn_nuevo = tk.Button(
            barra, text="Nuevo laberinto", font=("Segoe UI", 9, "bold"),
            bg="#e2e8f0", fg="#0f172a", relief="groove", padx=8, pady=3,
            command=self.nuevo_laberinto
        )
        self.btn_nuevo.pack(side="left", padx=4)

        self.btn_resolver = tk.Button(
            barra, text="Resolver automático", font=("Segoe UI", 9, "bold"),
            bg="#3b82f6", fg="white", activebackground="#2563eb",
            relief="groove", padx=8, pady=3, command=self.resolver_automatico
        )
        self.btn_resolver.pack(side="left", padx=4)

        self.btn_detener = tk.Button(
            barra, text="Detener", font=("Segoe UI", 9),
            bg="#fca5a5", fg="#7f1d1d", state="disabled",
            relief="groove", padx=6, pady=3, command=self.detener_animacion
        )
        self.btn_detener.pack(side="left", padx=4)

        self.btn_stats = tk.Button(
            barra, text="Ver Estadísticas", font=("Segoe UI", 9, "bold"),
            bg="#10b981", fg="white", activebackground="#059669",
            relief="groove", padx=8, pady=3, command=self.mostrar_estadisticas
        )
        self.btn_stats.pack(side="left", padx=6)

        # Leyenda de salidas
        tk.Label(barra, text="  S1: Rojo  S2: Naranja", font=("Segoe UI", 8, "bold"),
                 fg="#475569", bg="#f1f5f9").pack(side="right", padx=6)

        # ---------- Canvas del Laberinto ----------
        ancho = self.lab.columnas * TAM_CELDA
        alto = self.lab.filas * TAM_CELDA
        self.canvas = tk.Canvas(root, width=ancho, height=alto, bg=COLOR_PARED, highlightthickness=0)
        self.canvas.pack(padx=10, pady=6)

        # ---------- Barra de Estado Inferior ----------
        frame_estado = tk.Frame(root, bg="#f8fafc", padx=10, pady=6)
        frame_estado.pack(fill="x")

        self.label_estado = tk.Label(
            frame_estado, font=("Segoe UI", 9), justify="left", anchor="w",
            text="Movete con flechas o WASD. Presioná 'Resolver automático' para explorar el laberinto.",
            bg="#f8fafc", fg="#334155"
        )
        self.label_estado.pack(side="left", fill="x", expand=True)

        self.root.bind("<Key>", self._tecla_presionada)

        self._dibujar_laberinto()
        self._dibujar_jugador()

    # ==================================================================
    # ALGORITMO: Backtracking recursivo que recorre todo y vuelve
    # ==================================================================
    def _explorar(self, pos, camino, visitadas, pasos, salidas_encontradas, metricas):
        """
        Función recursiva pura con backtracking:
        1. Recorre TODO el laberinto visitando cada pasillo y callejón sin dar vueltas
           (almacena en 'visitadas' las celdas ya pisadas).
        2. CASOS BASE:
           - Celda fuera del mapa o pared (no transitable).
           - Celda ya visitada previamente (evita ciclos y dar vueltas innecesarias).
        3. AVANCE:
           - Marca la celda en visitadas y la agrega al camino actual.
           - Si es una salida (SALIDA1 o SALIDA2), guarda la ruta completa y cantidad de pasos.
           - Llama recursivamente a sus 4 direcciones vecinas transitables no visitadas.
        4. CASO BASE DE RETROCESO (callejón sin salida):
           - 'Cuando no puedo ir hacia la izquierda, abajo, derecha o arriba, voy hacia atrás'.
           - Desapila la celda de camino y genera el evento 'R' de retroceso.
           - Al finalizar todas las ramas, la recursión retrocede completamente
             hasta volver al punto de partida (1, 1).
        """
        metricas["llamadas"] += 1

        # CASO BASE 1: No transitable (es pared o celda inexistente)
        if not self.lab.es_transitable(*pos):
            return

        # CASO BASE 2: Evitar dar vueltas en círculos (ya visitada en esta exploración)
        if pos in visitadas:
            return

        # --- AVANCE ---
        visitadas.add(pos)
        camino.append(pos)
        pasos.append(("A", pos))
        metricas["avances"] += 1

        # Si encontramos una meta, guardamos la solución encontrada desde inicio
        if self.lab.es_meta(*pos):
            meta_tipo = self.lab.valor(*pos)
            cant_pasos = len(camino) - 1
            salidas_encontradas.append({
                "ruta": list(camino),
                "salida": meta_tipo,
                "pasos": cant_pasos
            })

        # Explorar en las 4 direcciones (arriba, derecha, abajo, izquierda)
        movimientos_posibles = 0
        for dr, dc in DIRECCIONES:
            sig = (pos[0] + dr, pos[1] + dc)
            if self.lab.es_transitable(*sig) and sig not in visitadas:
                movimientos_posibles += 1
                self._explorar(sig, camino, visitadas, pasos, salidas_encontradas, metricas)

        # CASO BASE DE RETROCESO (callejón sin salida):
        # Cuando no puedo ir hacia ninguna dirección válida, retorno
        if movimientos_posibles == 0 and not self.lab.es_meta(*pos):
            metricas["callejones"] += 1

        # --- RETROCESO (BACKTRACKING) ---
        # Desapila del camino actual y vuelve hacia atrás
        camino.pop()
        pasos.append(("R", pos))
        metricas["retrocesos"] += 1

    # ------------------------------------------------------------
    # Dibujo del Laberinto y Elementos
    # ------------------------------------------------------------
    def _color_de(self, valor):
        if valor == PARED:
            return COLOR_PARED
        if valor == INICIO:
            return COLOR_INICIO
        if valor == SALIDA1:
            return COLOR_SALIDA1
        if valor == SALIDA2:
            return COLOR_SALIDA2
        return COLOR_LIBRE

    def _dibujar_laberinto(self):
        self.canvas.delete("all")
        for (r, c), valor in self.lab.celdas.items():
            x0, y0 = c * TAM_CELDA, r * TAM_CELDA
            x1, y1 = x0 + TAM_CELDA, y0 + TAM_CELDA
            color = self._color_de(valor)

            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=color, outline="", tags="celda"
            )

            # Letras identificatorias en Inicio y Salidas
            if valor == INICIO:
                self.canvas.create_text(
                    x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2,
                    text="I", fill="white", font=("Segoe UI", 9, "bold"), tags="texto_fijo"
                )
            elif valor == SALIDA1:
                self.canvas.create_text(
                    x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2,
                    text="S1", fill="white", font=("Segoe UI", 8, "bold"), tags="texto_fijo"
                )
            elif valor == SALIDA2:
                self.canvas.create_text(
                    x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2,
                    text="S2", fill="white", font=("Segoe UI", 8, "bold"), tags="texto_fijo"
                )

    def _pintar_celda(self, pos, color, tag="marca"):
        r, c = pos
        if self.lab.valor(r, c) in (PARED, INICIO):
            return
        x0, y0 = c * TAM_CELDA, r * TAM_CELDA
        x1, y1 = x0 + TAM_CELDA, y0 + TAM_CELDA
        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=color, outline="", tags=tag
        )

        val = self.lab.valor(r, c)
        if val in (SALIDA1, SALIDA2):
            txt = "S1" if val == SALIDA1 else "S2"
            self.canvas.create_text(
                x0 + TAM_CELDA // 2, y0 + TAM_CELDA // 2,
                text=txt, fill="white", font=("Segoe UI", 8, "bold"), tags="texto_meta"
            )

    def _dibujar_jugador(self):
        self.canvas.delete("jugador")
        r, c = self.jugador
        x0, y0 = c * TAM_CELDA, r * TAM_CELDA
        m = 4
        self.canvas.create_oval(
            x0 + m, y0 + m, x0 + TAM_CELDA - m, y0 + TAM_CELDA - m,
            fill=COLOR_JUGADOR, outline="white", width=1, tags="jugador"
        )

    # ------------------------------------------------------------
    # Modo Manual (Flechas / WASD)
    # ------------------------------------------------------------
    def _tecla_presionada(self, evento):
        if self.animando:
            return
        direccion = TECLAS.get(evento.keysym)
        if not direccion:
            return
        dr, dc = direccion
        nr, nc = self.jugador[0] + dr, self.jugador[1] + dc
        if not self.lab.es_transitable(nr, nc):
            return

        self.jugador = (nr, nc)
        self.pasos_manuales += 1
        self._dibujar_jugador()

        if self.lab.es_meta(nr, nc):
            meta_alcanzada = self.lab.valor(nr, nc).upper()
            self.label_estado.config(
                text=f"¡Llegaste a {meta_alcanzada} en {self.pasos_manuales} pasos manuales! "
                     f"Podés ver las estadísticas o crear un nuevo laberinto."
            )

    # ------------------------------------------------------------
    # Modo Automático con Recorrido Total y Trayecto Óptimo
    # ------------------------------------------------------------
    def resolver_automatico(self):
        if self.animando:
            return

        self.canvas.delete("marca")
        self.canvas.delete("texto_meta")
        self.animando = True
        self._cancelar_animacion = False
        self.btn_resolver.config(state="disabled")
        self.btn_nuevo.config(state="disabled")
        self.btn_detener.config(state="normal")

        self.label_estado.config(
            text="Fase 1: Recorriendo todo el laberinto por backtracking y volviendo al inicio..."
        )

        pasos_exploracion = []
        salidas_encontradas = []
        metricas = {
            "llamadas": 0,
            "avances": 0,
            "retrocesos": 0,
            "callejones": 0,
        }
        visitadas = set()

        # 1. Exploración recursiva: recorre todo, guarda celdas visitadas y vuelve a la partida
        self._explorar(self.lab.inicio, [], visitadas, pasos_exploracion, salidas_encontradas, metricas)

        # 2. Determinar la salida más óptima (menor cantidad de pasos)
        optimo = min(salidas_encontradas, key=lambda c: c["pasos"]) if salidas_encontradas else None

        self.ultima_resolucion = {
            "caminos": salidas_encontradas,
            "optimo": optimo,
            "metricas": metricas,
            "total_visitadas": len(visitadas)
        }

        # 3. Iniciar animación: Fase 1 (Exploración total y regreso) seguida de Fase 2 (Ruta óptima)
        self._reproducir_exploracion(pasos_exploracion, 0, optimo)

    def detener_animacion(self):
        """Detiene la animación en curso y finaliza de inmediato mostrando el resultado."""
        if not self.animando:
            return
        self._cancelar_animacion = True
        if self._despues_id:
            self.root.after_cancel(self._despues_id)
            self._despues_id = None
        if self.ultima_resolucion:
            self._finalizar_animacion(self.ultima_resolucion["optimo"])

    def _reproducir_exploracion(self, pasos, indice, optimo):
        """Fase 1: Muestra cómo la recursión recorre todo el laberinto y vuelve al inicio."""
        if self._cancelar_animacion:
            return

        if indice >= len(pasos):
            # Fase 1 terminada: ya recorrió todo y volvió a la casilla de inicio (1, 1).
            self.jugador = self.lab.inicio
            self._dibujar_jugador()

            if optimo:
                salida_nom = optimo["salida"].upper()
                pasos_opt = optimo["pasos"]
                self.label_estado.config(
                    text=f"Fase 1 completada (de regreso en la partida). "
                         f"Iniciando camino óptimo hacia {salida_nom} ({pasos_opt} pasos)..."
                )
                # Pequeña pausa antes de iniciar el trayecto óptimo hacia la meta
                self._despues_id = self.root.after(
                    350, self._reproducir_camino_optimo, optimo["ruta"], 0, optimo
                )
            else:
                self._finalizar_animacion(None)
            return

        evento, pos = pasos[indice]
        color = COLOR_AVANCE if evento == "A" else COLOR_RETROCESO
        self._pintar_celda(pos, color)

        # Actualizar jugador durante la exploración
        self.jugador = pos
        self._dibujar_jugador()

        retardo = RETARDO_MS
        self._despues_id = self.root.after(
            retardo, self._reproducir_exploracion, pasos, indice + 1, optimo
        )

    def _reproducir_camino_optimo(self, ruta, indice, optimo):
        """Fase 2: Desde el inicio, recorre paso a paso el camino más óptimo hacia la meta ganadora."""
        if self._cancelar_animacion:
            return

        if indice >= len(ruta):
            self._finalizar_animacion(optimo)
            return

        pos = ruta[indice]
        self._pintar_celda(pos, COLOR_RUTA)
        self.jugador = pos
        self._dibujar_jugador()

        retardo = RETARDO_OPTIMO_MS
        self._despues_id = self.root.after(
            retardo, self._reproducir_camino_optimo, ruta, indice + 1, optimo
        )

    def _finalizar_animacion(self, optimo):
        self.animando = False
        self._cancelar_animacion = False
        self.btn_resolver.config(state="normal")
        self.btn_nuevo.config(state="normal")
        self.btn_detener.config(state="disabled")

        if optimo:
            # Asegurar que toda la ruta óptima quede resaltada
            for pos in optimo["ruta"]:
                self._pintar_celda(pos, COLOR_RUTA)
            self.jugador = optimo["ruta"][-1]
            self._dibujar_jugador()

            salida_nom = optimo["salida"].upper()
            pasos_opt = optimo["pasos"]
            self.label_estado.config(
                text=f"¡Completado! Se recorrió todo el laberinto. "
                     f"Llegada más óptima: {salida_nom} en {pasos_opt} pasos. "
                     f"Presioná 'Ver Estadísticas' para ver el informe."
            )
        else:
            self.label_estado.config(text="No se encontraron salidas transitables.")

    # ------------------------------------------------------------
    # Menú / Ventana de Estadísticas
    # ------------------------------------------------------------
    def mostrar_estadisticas(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Estadísticas del Algoritmo Recursivo")
        ventana.geometry("520x480")
        ventana.resizable(False, False)
        ventana.configure(bg="#f8fafc")
        ventana.transient(self.root)
        ventana.grab_set()

        # Encabezado
        encabezado = tk.Frame(ventana, bg="#1e293b", padx=16, pady=12)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado, text="Estadísticas de Resolución",
            font=("Segoe UI", 13, "bold"), fg="white", bg="#1e293b"
        ).pack(anchor="w")
        tk.Label(
            encabezado, text="Análisis del recorrido recursivo con backtracking",
            font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b"
        ).pack(anchor="w")

        cuerpo = tk.Frame(ventana, bg="#f8fafc", padx=16, pady=12)
        cuerpo.pack(fill="both", expand=True)

        if not self.ultima_resolucion or not self.ultima_resolucion["caminos"]:
            tk.Label(
                cuerpo, text="Aún no se ha ejecutado la resolución automática.\n"
                             "Presioná '▶ Resolver automático' para generar las estadísticas.",
                font=("Segoe UI", 10), fg="#64748b", bg="#f8fafc", justify="center"
            ).pack(expand=True)
            return

        res = self.ultima_resolucion
        optimo = res["optimo"]
        caminos = res["caminos"]
        metricas = res["metricas"]
        total_visitadas = res.get("total_visitadas", 0)

        # 1. Tarjeta de Solución Óptima
        card_opt = tk.LabelFrame(
            cuerpo, text="Solución Más Óptima ", font=("Segoe UI", 9, "bold"),
            bg="#f8fafc", fg="#0f172a", padx=10, pady=8
        )
        card_opt.pack(fill="x", pady=(0, 10))

        salida_opt = optimo["salida"].upper()
        pasos_opt = optimo["pasos"]
        tk.Label(
            card_opt,
            text=f"• Salida ganadora: {salida_opt}\n"
                 f"• Cantidad de pasos óptima: {pasos_opt} pasos",
            font=("Segoe UI", 10, "bold"), fg="#16a34a", bg="#f8fafc", justify="left"
        ).pack(anchor="w")

        # 2. Tarjeta de Comparativa de Salidas
        card_comp = tk.LabelFrame(
            cuerpo, text="Comparativa de Salidas ", font=("Segoe UI", 9, "bold"),
            bg="#f8fafc", fg="#0f172a", padx=10, pady=8
        )
        card_comp.pack(fill="x", pady=(0, 10))

        cams_s1 = [c for c in caminos if c["salida"] == SALIDA1]
        cams_s2 = [c for c in caminos if c["salida"] == SALIDA2]
        min_s1 = min((c["pasos"] for c in cams_s1), default="No alcanzada")
        min_s2 = min((c["pasos"] for c in cams_s2), default="No alcanzada")

        texto_comp = (
            f"• SALIDA 1 (Rojo): Llegada en {min_s1} pasos\n"
            f"• SALIDA 2 (Naranja): Llegada en {min_s2} pasos\n"
            f"• Celdas transitables exploradas: {total_visitadas}"
        )
        tk.Label(
            card_comp, text=texto_comp,
            font=("Segoe UI", 9), fg="#334155", bg="#f8fafc", justify="left"
        ).pack(anchor="w")

        # 3. Tarjeta de Métricas de la Recursión
        card_rec = tk.LabelFrame(
            cuerpo, text="Métricas del Árbol de Recursión ", font=("Segoe UI", 9, "bold"),
            bg="#f8fafc", fg="#0f172a", padx=10, pady=8
        )
        card_rec.pack(fill="x", pady=(0, 10))

        texto_rec = (
            f"• Total de llamadas recursivas: {metricas['llamadas']}\n"
            f"• Avances explorados: {metricas['avances']}\n"
            f"• Retrocesos ejecutados (backtracks hasta inicio): {metricas['retrocesos']}\n"
            f"• Callejones sin salida donde retrocedió: {metricas['callejones']}"
        )
        tk.Label(
            card_rec, text=texto_rec,
            font=("Segoe UI", 9), fg="#334155", bg="#f8fafc", justify="left"
        ).pack(anchor="w")

        # Botón de Cerrar
        tk.Button(
            ventana, text="Cerrar", font=("Segoe UI", 9, "bold"),
            bg="#0f172a", fg="white", padx=16, pady=4,
            command=ventana.destroy
        ).pack(pady=(0, 10))

    # ------------------------------------------------------------
    def nuevo_laberinto(self):
        if self.animando:
            return
        self.lab = Laberinto(self.lab.filas, self.lab.columnas)
        self.jugador = self.lab.inicio
        self.pasos_manuales = 0
        self.ultima_resolucion = None
        self._cancelar_animacion = False
        self._dibujar_laberinto()
        self._dibujar_jugador()
        self.label_estado.config(
            text="Laberinto nuevo listo. Usá flechas/WASD o presioná 'Resolver automático'."
        )
