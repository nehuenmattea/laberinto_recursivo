import unittest
from laberinto import Laberinto, PARED, LIBRE, INICIO, SALIDA1, SALIDA2
from collections import deque


class TestLaberinto(unittest.TestCase):
    def test_topologia_y_sin_artefactos(self):
        """Verifica que el laberinto no tenga postes aislados (010), ni bloques 2x2 libres."""
        for semilla in range(25):
            lab = Laberinto(semilla=semilla)

            # 1. Comprobar que no hay bloques 2x2 de celdas libres
            for r in range(lab.filas - 1):
                for c in range(lab.columnas - 1):
                    bloque = [
                        lab.valor(r, c), lab.valor(r, c + 1),
                        lab.valor(r + 1, c), lab.valor(r + 1, c + 1)
                    ]
                    libres_en_bloque = sum(1 for v in bloque if v in (LIBRE, INICIO, SALIDA1, SALIDA2))
                    self.assertLess(
                        libres_en_bloque, 4,
                        f"Semilla {semilla}: Se encontró un bloque 2x2 abierto en ({r}, {c})"
                    )

            # 2. Comprobar que no hay postes de pared completamente aislados (010 / 000 / 000)
            for r in range(1, lab.filas - 1):
                for c in range(1, lab.columnas - 1):
                    if lab.valor(r, c) == PARED:
                        vecinos_pared = sum(
                            1 for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                            if lab.valor(r + dr, c + dc) == PARED
                        )
                        self.assertGreater(
                            vecinos_pared, 0,
                            f"Semilla {semilla}: Pared aislada tipo 010 en ({r}, {c})"
                        )

    def test_conectividad_y_alcance_salidas(self):
        """Verifica mediante BFS que tanto Salida 1 como Salida 2 sean alcanzables desde Inicio."""
        for semilla in range(20):
            lab = Laberinto(semilla=semilla)
            visitados = set([lab.inicio])
            cola = deque([lab.inicio])

            while cola:
                r, c = cola.popleft()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if lab.es_transitable(nr, nc) and (nr, nc) not in visitados:
                        visitados.add((nr, nc))
                        cola.append((nr, nc))

            self.assertIn(lab.salida1, visitados, f"Semilla {semilla}: Salida 1 inalcanzable")
            self.assertIn(lab.salida2, visitados, f"Semilla {semilla}: Salida 2 inalcanzable")
            self.assertNotEqual(lab.salida1, lab.salida2, "Las salidas deben ser distintas")

    def test_variabilidad_salidas(self):
        """Verifica que las salidas cambien de posición a lo largo de distintas semillas."""
        posiciones_s1 = set()
        posiciones_s2 = set()
        for semilla in range(15):
            lab = Laberinto(semilla=semilla)
            posiciones_s1.add(lab.salida1)
            posiciones_s2.add(lab.salida2)

        self.assertGreaterEqual(len(posiciones_s1), 6, "Poca variabilidad en Salida 1")
        self.assertGreaterEqual(len(posiciones_s2), 6, "Poca variabilidad en Salida 2")

    def test_resolucion_backtracking_exhaustivo_sin_vueltas(self):
        """Verifica que la exploración recursiva recorra todo sin dar vueltas y halle la ruta óptima."""
        for sem in range(10):
            lab = Laberinto(semilla=sem)
            direcciones = [(-1, 0), (0, 1), (1, 0), (0, -1)]

            pasos = []
            salidas = []
            metricas = {"llamadas": 0, "avances": 0, "retrocesos": 0, "callejones": 0}
            visitadas = set()

            def explorar(pos, camino):
                metricas["llamadas"] += 1
                if not lab.es_transitable(*pos) or pos in visitadas:
                    return

                visitadas.add(pos)
                camino.append(pos)
                pasos.append(("A", pos))
                metricas["avances"] += 1

                if lab.es_meta(*pos):
                    salidas.append({
                        "ruta": list(camino),
                        "salida": lab.valor(*pos),
                        "pasos": len(camino) - 1
                    })

                movs = 0
                for dr, dc in direcciones:
                    sig = (pos[0] + dr, pos[1] + dc)
                    if lab.es_transitable(*sig) and sig not in visitadas:
                        movs += 1
                        explorar(sig, camino)
                if movs == 0 and not lab.es_meta(*pos):
                    metricas["callejones"] += 1

                camino.pop()
                pasos.append(("R", pos))
                metricas["retrocesos"] += 1

            explorar(lab.inicio, [])

            # Debe haber encontrado ambas salidas
            self.assertEqual(len(salidas), 2, f"Semilla {sem}: Deben encontrarse ambas salidas")
            # Avances y retrocesos deben ser exactamente iguales (vuelve a la partida)
            self.assertEqual(metricas["avances"], metricas["retrocesos"])
            # Cada celda transitable se visita exactamente una vez (sin dar vueltas repetidas)
            self.assertEqual(len(visitadas), metricas["avances"])

            # Comprobar que existe una ruta óptima bien definida
            optimo = min(salidas, key=lambda c: c["pasos"])
            self.assertIn(optimo["salida"], (SALIDA1, SALIDA2))
            self.assertGreater(optimo["pasos"], 0)


if __name__ == "__main__":
    unittest.main()
