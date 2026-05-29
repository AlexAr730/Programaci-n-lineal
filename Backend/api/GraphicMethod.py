import numpy as np
import plotly.graph_objs as go
from scipy.optimize import linprog
from plotly.io import to_html
import pandas as pd
import time
from IPython.display import clear_output, display

def metodo_grafico(objetivo, restricciones, limites=(0,10,0,10), maximizar=True):
    x_min, x_max, y_min, y_max = limites
    x = np.linspace(x_min, x_max, 400)
    y = np.linspace(y_min, y_max, 400)
    X, Y = np.meshgrid(x, y)

    mascara = np.ones_like(X, dtype=bool)
    for a, b, cst, sentido in restricciones:
        if sentido == '<=':
            mascara &= (a * X + b * Y <= cst)
        elif sentido == '>=':
            mascara &= (a * X + b * Y >= cst)
        elif sentido == '=':
            mascara &= np.isclose(a * X + b * Y, cst, atol=1e-3)

    fig = go.Figure()
    

    for i, (a, b, cst, sentido) in enumerate(restricciones):
        if b != 0:  
            y_start = (cst - a * x_min) / b
            y_end = (cst - a * x_max) / b
        
            puntos_interseccion = []
            
            y_at_xmin = (cst - a * x_min) / b
            if y_min <= y_at_xmin <= y_max:
                puntos_interseccion.append((x_min, y_at_xmin))
            

            y_at_xmax = (cst - a * x_max) / b
            if y_min <= y_at_xmax <= y_max:
                puntos_interseccion.append((x_max, y_at_xmax))
            

            if a != 0:
                x_at_ymin = (cst - b * y_min) / a
                if x_min <= x_at_ymin <= x_max:
                    puntos_interseccion.append((x_at_ymin, y_min))
            

            if a != 0:
                x_at_ymax = (cst - b * y_max) / a
                if x_min <= x_at_ymax <= x_max:
                    puntos_interseccion.append((x_at_ymax, y_max))
            

            puntos_interseccion = list(set(puntos_interseccion))
            
            if len(puntos_interseccion) >= 2:

                puntos_interseccion = sorted(puntos_interseccion)[:2]
                x_vals = [p[0] for p in puntos_interseccion]
                y_vals = [p[1] for p in puntos_interseccion]
                
                estilo = 'dash' if sentido != '=' else 'solid'
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, mode='lines',
                    name=f"{a}x + {b}y {sentido} {cst}",
                    line=dict(dash=estilo, width=2)
                ))
        
        else:  
            if a != 0:
                x_val = cst / a
                if x_min <= x_val <= x_max:
                    estilo = 'dash' if sentido != '=' else 'solid'
                    fig.add_trace(go.Scatter(
                        x=[x_val, x_val], y=[y_min, y_max], mode='lines',
                        name=f"x = {x_val}",
                        line=dict(dash=estilo, width=2)
                    ))

    fig.add_trace(go.Contour(
        x=x, y=y, z=mascara.astype(int),
        showscale=False, opacity=0.5, 
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'lightgreen']],
        hoverinfo='skip', name='Región factible',
        contours=dict(coloring='fill', showlines=False)
    ))

    c = np.array(objetivo)
    if maximizar:
        c = -c
    
    A_ub = []
    b_ub = []
    A_eq = []
    b_eq = []
    
    for a, b, cst, sentido in restricciones:
        if sentido == '<=':
            A_ub.append([a, b])
            b_ub.append(cst)
        elif sentido == '>=':
            A_ub.append([-a, -b])
            b_ub.append(-cst)
        elif sentido == '=':
            A_eq.append([a, b])
            b_eq.append(cst)
    
    res = linprog(c, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                  A_eq=A_eq if A_eq else None, b_eq=b_eq if b_eq else None,
                  bounds=[(x_min, x_max), (y_min, y_max)])
    
    if res.success:
        x_opt, y_opt = res.x
        valor_opt = np.dot(objetivo, res.x)
        
        fig.add_trace(go.Scatter(
            x=[x_opt], y=[y_opt], mode='markers+text',
            marker=dict(color='red', size=12),
            text=[f"Óptimo ({x_opt:.2f}, {y_opt:.2f})<br>Valor: {valor_opt:.2f}"],
            textposition="top right",
            name='Solución óptima'
        ))
        
        fig.update_layout(
            title='Programación Lineal (Método Gráfico)',
            xaxis_title='x',
            yaxis_title='y',
            legend=dict(x=0.01, y=0.99),
            xaxis=dict(range=[x_min, x_max]),
            yaxis=dict(range=[y_min, y_max])
        )
        
        plot_html = to_html(fig, full_html=False)
        return {
            "plot_html": plot_html,
            "solucion": (x_opt, y_opt),
            "valor_optimo": valor_opt,
            "restricciones": restricciones,
            "objetivo": objetivo
        }
    else:
        fig.update_layout(
            title='Programación Lineal (Método Gráfico)',
            xaxis_title='x',
            yaxis_title='y',
            legend=dict(x=0.01, y=0.99),
            xaxis=dict(range=[x_min, x_max]),
            yaxis=dict(range=[y_min, y_max])
        )
        
        plot_html = to_html(fig, full_html=False)
        return {
            "plot_html": plot_html,
            "solucion": None,
            "valor_optimo": None,
            "restricciones": restricciones,
            "objetivo": objetivo
        }
