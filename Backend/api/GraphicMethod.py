import numpy as np
import plotly.graph_objs as go
from scipy.optimize import linprog
import json
from plotly.utils import PlotlyJSONEncoder

def calcular_limites(restricciones, default_max=10.0):
    puntos = [(0.0, 0.0)]
    for a, b, cst, _ in restricciones:
        if a != 0: puntos.append((float(cst / a), 0.0))
        if b != 0: puntos.append((0.0, float(cst / b)))
            
    n = len(restricciones)
    for i in range(n):
        for j in range(i + 1, n):
            a1, b1, cst1, _ = restricciones[i]
            a2, b2, cst2, _ = restricciones[j]
            det = a1 * b2 - b1 * a2
            if abs(det) > 1e-5:
                x_int = (cst1 * b2 - b1 * cst2) / det
                y_int = (a1 * cst2 - cst1 * a2) / det
                puntos.append((float(x_int), float(y_int)))
                
    puntos_validos = []
    for px, py in puntos:
        if np.isnan(px) or np.isnan(py) or np.isinf(px) or np.isinf(py):
            continue
        if px >= -0.5 and py >= -0.5 and px < 1e5 and py < 1e5:
            puntos_validos.append((px, py))
            
    if not puntos_validos:
        return 0.0, float(default_max), 0.0, float(default_max)
        
    x_coords = [p[0] for p in puntos_validos]
    y_coords = [p[1] for p in puntos_validos]
    
    x_min = min(0.0, float(np.floor(min(x_coords))))
    y_min = min(0.0, float(np.floor(min(y_coords))))
    x_max = max(float(default_max), float(max(x_coords) * 1.2))
    y_max = max(float(default_max), float(max(y_coords) * 1.2))
    
    return x_min, float(np.ceil(x_max)), y_min, float(np.ceil(y_max))


def agregar_linea(fig, a, b, d, x_min, x_max, y_min, y_max, nombre, estilo='solid', color=None, ancho=2):
    if b != 0:
        puntos = []
        y_at_xmin = (d - a * x_min) / b
        if y_min <= y_at_xmin <= y_max: puntos.append((x_min, y_at_xmin))
        y_at_xmax = (d - a * x_max) / b
        if y_min <= y_at_xmax <= y_max: puntos.append((x_max, y_at_xmax))
        if a != 0:
            x_at_ymin = (d - b * y_min) / a
            if x_min <= x_at_ymin <= x_max: puntos.append((x_at_ymin, y_min))
            x_at_ymax = (d - b * y_max) / a
            if x_min <= x_at_ymax <= x_max: puntos.append((x_at_ymax, y_max))
        
        puntos_unicos = []
        for p in puntos:
            if not any(np.allclose(p, pu, atol=1e-5) for pu in puntos_unicos): puntos_unicos.append(p)
                
        if len(puntos_unicos) >= 2:
            puntos_unicos = sorted(puntos_unicos, key=lambda p: p[0])[:2]
            line_dict = dict(dash=estilo, width=ancho)
            if color: line_dict['color'] = color
            fig.add_trace(go.Scatter(
                x=[p[0] for p in puntos_unicos], y=[p[1] for p in puntos_unicos], 
                mode='lines', name=nombre, line=line_dict
            ))
    else:
        if a != 0:
            x_val = d / a
            if x_min <= x_val <= x_max:
                line_dict = dict(dash=estilo, width=ancho)
                if color: line_dict['color'] = color
                fig.add_trace(go.Scatter(
                    x=[x_val, x_val], y=[y_min, y_max], mode='lines', name=nombre, line=line_dict
                ))


def metodo_grafico(objetivo, restricciones, limites=None, maximizar=True):
    if limites is None:
        limites = calcular_limites(restricciones)
        
    x_min, x_max, y_min, y_max = limites
    
    # 1. ENCONTRAR VÉRTICES DE LA REGIÓN FACTIBLE
    puntos_interseccion = [(0.0, 0.0)]
    for a, b, cst, _ in restricciones:
        if a != 0: puntos_interseccion.append((float(cst / a), 0.0))
        if b != 0: puntos_interseccion.append((0.0, float(cst / b)))
            
    n = len(restricciones)
    for i in range(n):
        for j in range(i + 1, n):
            a1, b1, cst1, _ = restricciones[i]
            a2, b2, cst2, _ = restricciones[j]
            det = a1 * b2 - b1 * a2
            if abs(det) > 1e-5:
                x_int = (cst1 * b2 - b1 * cst2) / det
                y_int = (a1 * cst2 - cst1 * a2) / det
                puntos_interseccion.append((float(x_int), float(y_int)))

    puntos_interseccion.extend([(x_min, 0.0), (x_max, 0.0), (0.0, y_min), (0.0, y_max)])

    vertices_factibles = []
    for px, py in puntos_interseccion:
        if px < -1e-5 or py < -1e-5: 
            continue
        cumple_todas = True
        for a, b, cst, sentido in restricciones:
            val = a * px + b * py
            if sentido == '<=' and val > cst + 1e-5: cumple_todas = False
            elif sentido == '>=' and val < cst - 1e-5: cumple_todas = False
            elif sentido == '=' and not np.isclose(val, cst, atol=1e-3): cumple_todas = False
        if cumple_todas:
            if not any(np.allclose([px, py], v, atol=1e-4) for v in vertices_factibles):
                vertices_factibles.append((px, py))

    fig = go.Figure()

    # 2. SOMBREAR LA REGIÓN FACTIBLE (Azul traslúcido)
    if len(vertices_factibles) >= 3:
        cx = np.mean([p[0] for p in vertices_factibles])
        cy = np.mean([p[1] for p in vertices_factibles])
        vertices_factibles.sort(key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))
        vertices_factibles.append(vertices_factibles[0])
        
        fig.add_trace(go.Scatter(
            x=[p[0] for p in vertices_factibles], 
            y=[p[1] for p in vertices_factibles],
            fill="toself",
            fillcolor="rgba(0, 123, 255, 0.3)",  
            line=dict(color="rgba(0, 123, 255, 0)"),
            name="Región Factible",
            hoverinfo="skip"
        ))

    # 3. DIBUJAR LÍNEAS DE RESTRICCIÓN
    for a, b, cst, sentido in restricciones:
        nombre = f"{a}x + {b}y {sentido} {cst}" if b != 0 else f"x = {cst/a:.2f}"
        agregar_linea(fig, a, b, cst, x_min, x_max, y_min, y_max, nombre, estilo='solid', ancho=2)

    # 4. RESOLVER OPTIMIZACIÓN
    c = np.array(objetivo)
    if maximizar: c = -c
    
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    for a, b, cst, sentido in restricciones:
        if sentido == '<=':
            A_ub.append([a, b]); b_ub.append(cst)
        elif sentido == '>=':
            A_ub.append([-a, -b]); b_ub.append(-cst)
        elif sentido == '=':
            A_eq.append([a, b]); b_eq.append(cst)
    
    res = linprog(c, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                  A_eq=A_eq if A_eq else None, b_eq=b_eq if b_eq else None,
                  bounds=[(0, x_max), (0, y_max)])
    
    if res.success:
        x_opt, y_opt = res.x
        valor_opt = np.dot(objetivo, res.x)
        
        fig.add_trace(go.Scatter(
            x=[x_opt], y=[y_opt], mode='markers+text',
            marker=dict(color='red', size=12, symbol='star'),
            text=[f"Óptimo ({x_opt:.2f}, {y_opt:.2f})<br>Z = {valor_opt:.2f}"],
            textposition="top right", name='Solución óptima'
        ))
        
        agregar_linea(fig, objetivo[0], objetivo[1], valor_opt, x_min, x_max, y_min, y_max,
                      nombre=f"Función Objetivo (Z = {valor_opt:.2f})", estilo='dash', color='purple', ancho=3)
    else:
        x_opt, y_opt, valor_opt = None, None, None

    fig.update_layout(
        title='Programación Lineal (Método Gráfico)',
        xaxis_title='Variable X', yaxis_title='Variable Y',
        legend=dict(x=0.01, y=0.99),
        xaxis=dict(range=[x_min, x_max], zeroline=True, zerolinewidth=1.5, zerolinecolor='black'),
        yaxis=dict(range=[y_min, y_max], zeroline=True, zerolinewidth=1.5, zerolinecolor='black'),
        template="plotly_white"
    )
    
    plot_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return {
        "plot_json": plot_json, 
        "solucion": (x_opt, y_opt) if res.success else None,
        "valor_optimo": valor_opt if res.success else None,
        "restricciones": restricciones,
        "objetivo": objetivo
    }