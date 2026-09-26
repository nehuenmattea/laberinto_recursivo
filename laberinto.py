import random

PARED = "pared"
LIBRE = "libre"
INICIO = "inicio"
SALIDA1 = "salida1"
SALIDA2 = "salida2"

FILAS_DEFECTO = 21
COLUMNAS_DEFECTO = 21


class Laberinto:
    def __init__(self, filas=FILAS_DEFECTO, columnas=COLUMNAS_DEFECTO, semilla=None):
        self.filas = filas
        self.columnas = columnas
        self.celdas = {}       # Diccionario (r, c) -> tipo
        self.inicio = (1, 1)
        self.salida1 = None
        self.salida2 = None
        self._generar(semilla)

    # ------------------------------------------------------------
    # Consultas sobre el diccionario (usadas por la GUI y el solver)
    # ------------------------------------------------------------
    def valor(self, r, c):
        """Devuelve qué hay en (r, c), o None si esa celda no existe."""
        return self.celdas.get((r, c))

    def es_transitable(self, r, c):
        """Combina 'está dentro del laberinto' y 'no es pared' en un solo chequeo."""
        return self.celdas.get((r, c)) not in (None, PARED)

    def es_meta(self, r, c):
        """Indica si la celda es alguna de las salidas configuradas."""
        return self.celdas.get((r, c)) in (SALIDA1, SALIDA2)

    # ------------------------------------------------------------
    # Generación del laberinto (RECURSIVO):
    # Algoritmo Recursive Backtracker 
    # ------------------------------------------------------------
    def _generar(self, semilla):
        rng = random.Random(semilla)

        # 1. Arrancamos el laberinto con TODO pared
        for r in range(self.filas):
            for c in range(self.columnas):
                self.celdas[(r, c)] = PARED

        # 2. Tallado recursivo celda a celda
        def tallar(r, c, ultima_dir=None):
            self.celdas[(r, c)] = LIBRE
            direcciones = [(-2, 0), (2, 0), (0, -2), (0, 2)]

            # Inercia direccional: mantener la dirección previa con cierta
            # probabilidad para crear pasillos fluidos y evitar giros continuos
            if ultima_dir and ultima_dir in direcciones and rng.random() < 0.65:
                otras = [d for d in direcciones if d != ultima_dir]
                rng.shuffle(otras)
                orden = [ultima_dir] + otras
            else:
                rng.shuffle(direcciones)
                orden = direcciones

            for dr, dc in orden:
                nr, nc = r + dr, c + dc
                if 0 < nr < self.filas - 1 and 0 < nc < self.columnas - 1:
                    if self.celdas[(nr, nc)] == PARED:
                        # Abre la pared intermedia y continúa tallando recursivamente
                        self.celdas[(r + dr // 2, c + dc // 2)] = LIBRE
                        tallar(nr, nc, (dr, dc))
            # Al no haber más direcciones posibles, la función retorna (retroceso)

        tallar(self.inicio[0], self.inicio[1])

        # 3. Apertura controlada de ciclos para permitir caminos alternativos
        # Se aplican restricciones estrictas para evitar celdas aisladas
        # (patrones como 010 / 000 / 000 o 0 / 01 / 00) y bloques abiertos 2x2.
        candidatos = []
        for r in range(1, self.filas - 1):
            for c in range(1, self.columnas - 1):
                if self.celdas[(r, c)] != PARED:
                    continue
                # Pared vertical entre dos pasillos libres
                if r % 2 == 1 and c % 2 == 0:
                    if self.celdas.get((r, c - 1)) == LIBRE and self.celdas.get((r, c + 1)) == LIBRE:
                        candidatos.append((r, c, 'v'))
                # Pared horizontal entre dos pasillos libres
                elif r % 2 == 0 and c % 2 == 1:
                    if self.celdas.get((r - 1, c)) == LIBRE and self.celdas.get((r + 1, c)) == LIBRE:
                        candidatos.append((r, c, 'h'))

        rng.shuffle(candidatos)
        ciclos_abiertos = 0
        max_ciclos = 3

        for r, c, tipo in candidatos:
            if ciclos_abiertos >= max_ciclos:
                break

            # (A) Chequeo: no formar un bloque 2x2 de celdas libres
            forma_2x2 = False
            for dr in (-1, 0):
                for dc in (-1, 0):
                    coords = [(r + dr + i, c + dc + j) for i in (0, 1) for j in (0, 1)]
                    if all(pos == (r, c) or self.celdas.get(pos) != PARED for pos in coords):
                        forma_2x2 = True
                        break
                if forma_2x2:
                    break
            if forma_2x2:
                continue

            # (B) Chequeo: no aislar postes de pared vecinos
            postes = [(r - 1, c), (r + 1, c)] if tipo == 'v' else [(r, c - 1), (r, c + 1)]
            aisla_poste = False
            for pr, pc in postes:
                paredes = sum(
                    1 for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                    if (pr + dr, pc + dc) != (r, c) and self.celdas.get((pr + dr, pc + dc)) == PARED
                )
                if paredes < 1:
                    aisla_poste = True
                    break
            if aisla_poste:
                continue

            self.celdas[(r, c)] = LIBRE
            ciclos_abiertos += 1

        # 4. Establecer Inicio
        self.celdas[self.inicio] = INICIO

        # 5. Salidas variables en distintos cuadrantes y callejones
        libres = [pos for pos, v in self.celdas.items() if v == LIBRE and pos != self.inicio]

        def vecinos_libres(pos):
            return sum(
                1 for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if self.celdas.get((pos[0] + dr, pos[1] + dc)) != PARED
            )

        callejones = [p for p in libres if vecinos_libres(p) == 1]

        def dist_m(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        candidatos_salidas = [p for p in callejones if dist_m(p, self.inicio) >= 14]
        if len(candidatos_salidas) < 2:
            candidatos_salidas = [p for p in libres if dist_m(p, self.inicio) >= 14]

        # Clasificación por cuadrantes
        mitad_r = self.filas // 2
        mitad_c = self.columnas // 2
        z_arriba_der = [p for p in candidatos_salidas if p[0] <= mitad_r and p[1] >= mitad_c]
        z_abajo_izq = [p for p in candidatos_salidas if p[0] >= mitad_r and p[1] <= mitad_c]
        z_abajo_der = [p for p in candidatos_salidas if p[0] >= mitad_r and p[1] >= mitad_c]

        zonas = [z for z in [z_arriba_der, z_abajo_izq, z_abajo_der] if z]
        if len(zonas) >= 2:
            rng.shuffle(zonas)
            s1 = rng.choice(zonas[0])
            resto = [p for z in zonas[1:] for p in z if dist_m(p, s1) >= 10]
            if not resto:
                resto = [p for p in candidatos_salidas if p != s1]
            s2 = rng.choice(resto)
        else:
            s1 = rng.choice(candidatos_salidas)
            resto = [p for p in candidatos_salidas if dist_m(p, s1) >= 10]
            if not resto:
                resto = [p for p in libres if p != s1]
            s2 = rng.choice(resto)

        self.celdas[s1] = SALIDA1
        self.celdas[s2] = SALIDA2
        self.salida1 = s1
        self.salida2 = s2
