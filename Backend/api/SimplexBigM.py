import copy
import time

class SimplexBigM:
    def __init__(self, objetivo, restricciones, maximizar=True, M=10**6, tol=1e-6):
        # Convertir minimización a maximización
        self.original_maximizar = maximizar
        if not maximizar:
            objetivo = tuple(-c for c in objetivo)
        self.objetivo = objetivo
        self.restricciones = restricciones
        self.maximizar = True  # Siempre maximizar internamente
        self.M = M
        self.tol = tol
        self.n = len(objetivo)
        self.m = len(restricciones)
        
        # Contar variables de holgura y artificiales
        self.n_slack = 0
        self.n_artificial = 0
        for rest in restricciones:
            tipo = rest[-1]
            if tipo == '<=':
                self.n_slack += 1
            elif tipo == '>=':
                self.n_slack += 1
                self.n_artificial += 1
            elif tipo == '=':
                self.n_artificial += 1
        
        self.total_vars = self.n + self.n_slack + self.n_artificial
        self.tabla = [[0.0] * (self.total_vars + 1) for _ in range(self.m + 1)]
        self.basicas = []
        self.iterations = 0
        self.max_iter = 1000
        self.resultado = None
        self.solucion = None
        self.estado = None
        self.historial = []  # Almacenar estado de cada iteración

    def construir_tabla_initial(self):
        # Fila objetivo: -c para maximización
        for j, coeff in enumerate(self.objetivo):
            self.tabla[0][j] = -coeff
        
        idx_s = self.n
        idx_a = self.n + self.n_slack
        # Llenar restricciones
        for i, rest in enumerate(self.restricciones):
            coef = rest[:-2]
            b = rest[-2]
            tipo = rest[-1]
            for j in range(self.n):
                self.tabla[i+1][j] = coef[j]
            self.tabla[i+1][self.total_vars] = b
            
            if tipo == '<=':
                self.tabla[i+1][idx_s] = 1.0
                self.basicas.append(idx_s)
                idx_s += 1
            elif tipo == '>=':
                self.tabla[i+1][idx_s] = -1.0
                self.tabla[i+1][idx_a] = 1.0
                self.basicas.append(idx_a)
                idx_s += 1
                idx_a += 1
            elif tipo == '=':
                self.tabla[i+1][idx_a] = 1.0
                self.basicas.append(idx_a)
                idx_a += 1
        
        # Penalización Big M
        for i in range(1, self.m+1):
            tipo = self.restricciones[i-1][-1]
            if tipo in ('>=', '='):
                for j in range(self.total_vars + 1):
                    self.tabla[0][j] += self.M * self.tabla[i][j]
        
        # Guardar estado inicial
        self.guardar_estado("Tabla Inicial")

    def guardar_estado(self, etapa, col_p=None, fila_p=None):
        estado = {
            "etapa": etapa,
            "iteracion": self.iterations,
            "tabla": copy.deepcopy(self.tabla),
            "basicas": copy.copy(self.basicas),
            "entra": col_p,
            "sale": fila_p
        }
        self.historial.append(estado)

    def imprimir_tabla(self, estado):
        print(f"\n{estado['etapa']} - Iteración {estado['iteracion']}")
        if estado['entra'] is not None and estado['sale'] is not None:
            var_salida = self.basicas[estado['sale']]
            print(f"Entra: x{estado['entra']+1}, Sale: fila {estado['sale']+1} (x{var_salida+1})")

        
        # Encabezados
        headers = []
        for j in range(self.total_vars):
            if j < self.n:
                headers.append(f"x{j+1}")
            elif j < self.n + self.n_slack:
                headers.append(f"s{j-self.n+1}")
            else:
                headers.append(f"a{j-self.n-self.n_slack+1}")
        headers.append("RHS")
        
        # Imprimir encabezados
        print(" " * 8 + "\t".join(headers))
        
        # Imprimir fila objetivo
        print("Obj\t" + "\t".join(f"{val:10.2f}" for val in estado['tabla'][0]))
        
        # Imprimir restricciones
        for i in range(1, self.m+1):
            # Identificar variable básica
            var_idx = estado['basicas'][i-1]
            var_name = ""
            if var_idx < self.n:
                var_name = f"x{var_idx+1}"
            elif var_idx < self.n + self.n_slack:
                var_name = f"s{var_idx-self.n+1}"
            else:
                var_name = f"a{var_idx-self.n-self.n_slack+1}"
                
            print(f"{var_name}\t" + "\t".join(f"{val:10.2f}" for val in estado['tabla'][i]))
    
    def animar_solucion(self, delay=1.0):
        print("\n--- ANIMACIÓN DEL MÉTODO SIMPLEX ---")
        for i, estado in enumerate(self.historial):
            print(f"\n{'='*50}\nPaso {i+1}: {estado['etapa']}")
            self.imprimir_tabla(estado)
            time.sleep(delay)
    
    def resolver(self):
        self.construir_tabla_initial()
        
        while self.iterations < self.max_iter:
            self.iterations += 1
            
            # Variable de entrada: indicador más negativo
            col_p = None
            min_val = 0
            for j in range(self.total_vars):
                if self.tabla[0][j] < min_val - self.tol:
                    # Verificar si hay coeficiente positivo en restricciones
                    for i in range(1, self.m+1):
                        if self.tabla[i][j] > self.tol:
                            min_val = self.tabla[0][j]
                            col_p = j
                            break
            
            if col_p is None:
                break
            
            # Variable de salida: prueba de razón mínima
            fila_p = None
            min_ratio = float('inf')
            for i in range(1, self.m+1):
                if self.tabla[i][col_p] > self.tol:
                    ratio = self.tabla[i][self.total_vars] / self.tabla[i][col_p]
                    if ratio < min_ratio - self.tol:
                        min_ratio = ratio
                        fila_p = i
            
            if fila_p is None:
                self.estado = 'inlimitado'
                return
            
            # Guardar estado antes del pivote
            self.guardar_estado("Antes del pivote", col_p, fila_p - 1)  # ← guarda el índice de fila
            
            # Operación de pivote
            pivot = self.tabla[fila_p][col_p]
            for j in range(self.total_vars + 1):
                self.tabla[fila_p][j] /= pivot
            
            for i in range(self.m + 1):
                if i == fila_p:
                    continue
                factor = self.tabla[i][col_p]
                for j in range(self.total_vars + 1):
                    self.tabla[i][j] -= factor * self.tabla[fila_p][j]
            
            # Actualizar variable básica
            self.basicas[fila_p-1] = col_p
            
            # Guardar estado después del pivote
            self.guardar_estado("Después del pivote")
        
        else:
            self.estado = 'max_iter'
            return
        
        # Verificar factibilidad
        for i, var in enumerate(self.basicas):
            if var >= self.n + self.n_slack:  # Si es variable artificial
                if abs(self.tabla[i+1][self.total_vars]) > self.tol:
                    self.estado = 'infactible'
                    return
        
        # Construir solución
        sol = [0.0] * self.n
        for i, var in enumerate(self.basicas):
            if var < self.n:
                sol[var] = self.tabla[i+1][self.total_vars]
        
        self.solucion = sol
        self.resultado = self.tabla[0][self.total_vars]
        self.estado = 'optimo'
        self.guardar_estado("Tabla Final")

    def obtener_solucion(self):
        # Ajustar valor objetivo según problema original
        valor_ajustado = self.resultado
        if not self.original_maximizar:
            valor_ajustado = valor_ajustado
        return self.solucion, valor_ajustado, self.estado


def analisis_sensibilidad(solver):
    tabla_final = solver.historial[-1]["tabla"]
    basicas = solver.historial[-1]["basicas"]
    n_vars = solver.n
    m_restricciones = solver.m
    total_vars = solver.total_vars
    n_slack = solver.n_slack  

    precios_sombra = []
    holguras = []

    for i in range(m_restricciones):
        if i < n_slack:  
            col_idx = n_vars + i
            coef = tabla_final[0][col_idx]
            precios_sombra.append(round(coef, 2))
        else:
            precios_sombra.append(0.0)  
    for i in range(m_restricciones):
        var_basica = basicas[i]
        rhs_val = tabla_final[i+1][total_vars]  

        if n_vars <= var_basica < n_vars + n_slack:
            holguras.append((f"s{var_basica - n_vars + 1}", round(rhs_val, 2)))
        elif var_basica < n_vars:
            holguras.append((f"x{var_basica + 1}", 0.0))  
        else:
            holguras.append((f"a{var_basica - n_vars - n_slack + 1}", 0.0))  

    return {
        "precios_sombra": precios_sombra,
        "holguras": holguras
    }

def solve_simplex_big_m(objetivo, restricciones, maximizar=True, animar=True):
    solver = SimplexBigM(objetivo, restricciones, maximizar)
    solver.resolver()
    sol, val, estado = solver.obtener_solucion()
    sensibilidad = analisis_sensibilidad(solver)
    
    if animar:
        solver.animar_solucion()
    
    return sol, val, estado, solver, sensibilidad

