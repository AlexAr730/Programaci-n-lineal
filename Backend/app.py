from flask import Flask, render_template
from api.GraphicMethod import metodo_grafico
from flask import request, jsonify
from api.functions import parse_objective_function
import ast
from api.SimplexBigM import solve_simplex_big_m

methods_available = {
    "Graphical Method": "Graphical Method",
    "Simplex Method": "Simplex Method",
}

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/results', methods=['POST'])
def results():
    print("Content-Type recibido:", request.content_type)

    data = request.get_json()
    type_of_method = data.get("method")
    objective_function = data.get("objectiveFunction")
    constraints = data.get("constraints")
    type_of_problem = data.get("problemType")
    boolean_type = None
    
    if type_of_problem == "max":
        boolean_type = True
    else:
        boolean_type = False

    only_constraint = [ast.literal_eval(c["value"]) for c in data["constraints"]]
    objective_coefficients =  tuple(parse_objective_function(objective_function))

    if type_of_method == "Graphical Method":
        result = metodo_grafico(objective_coefficients,only_constraint,limites = (0,10,0,10),maximizar = boolean_type)
        return jsonify({
        "plot_html": result["plot_html"], 
        "solucion": result["solucion"], 
        "valor_optimo": result["valor_optimo"], 
        "restricciones": result["restricciones"], 
        "objetivo": result["objetivo"]}), 200

    elif type_of_method == "Simplex M Method":
        sol, val, estado, solver, sensibilidad = solve_simplex_big_m(objective_coefficients,only_constraint, maximizar = boolean_type, animar = True)

        table_history = []
        for step in solver.historial:
            table = step["tabla"]
            enter = step["entra"]
            sale = step["sale"]
            etapa = step["etapa"]
            iteracion = step["iteracion"]
            basicas = step["basicas"]
            table_history.append({
                "table": table,
                "enter": enter,
                "sale": sale,
                "etapa": etapa,
                "iteracion": iteracion,
                "basicas": basicas
            })

        return jsonify({
            "table_history": table_history,
            "solucion": sol,
            "valor_optimo": val,
            "estado": estado,
            "sensibilidad": sensibilidad
        }), 200

    else:
        return jsonify({"error": "Método no válido"}), 400

@app.route('/results')
def results_get():
    return render_template("results.html")

@app.route('/simplex_results')
def simplex_results():
    return render_template("simplex_results.html")

if __name__ == '__main__':
    app.run(debug=True)

