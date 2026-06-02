// FUNCIÓN AUXILIAR: Encuentra y ejecuta cualquier script dentro de un elemento
function executeScriptsInElement(element) {
  const scriptElements = element.getElementsByTagName("script");

  for (let i = 0; i < scriptElements.length; i++) {
    const script = document.createElement("script");
    script.innerHTML = scriptElements[i].innerHTML;
    document.body.appendChild(script);
    scriptElements[i].parentNode.removeChild(scriptElements[i]);
  }
}

// Función para formatear valores
function formatValue(value) {
  if (value === null || value === undefined) {
    return "No encontrado";
  }
  if (typeof value === "number") {
    return value.toFixed(4);
  }
  if (Array.isArray(value)) {
    return `(${value.map((v) => v.toFixed(4)).join(", ")})`;
  }
  return value.toString();
}

// Función para formatear función objetivo
function formatObjective(objective) {
  if (Array.isArray(objective)) {
    return objective
      .map((coef, i) => {
        const variable = i === 0 ? "x" : "y";
        const sign = coef >= 0 ? "+" : "";
        return `${sign}${coef}${variable}`;
      })
      .join(" ")
      .replace(/^\+/, "");
  }
  return objective.toString();
}

document.addEventListener("DOMContentLoaded", function () {
  const resultDataString = localStorage.getItem("lp_result");

  if (resultDataString) {
    const resultData = JSON.parse(resultDataString);

    // Llenar los datos del resumen numérico
    if (document.getElementById("objetivo")) {
      document.getElementById("objetivo").textContent = formatObjective(resultData.objetivo);
    }
    if (document.getElementById("valor-optimo")) {
      document.getElementById("valor-optimo").textContent = formatValue(resultData.valor_optimo);
    }
    if (document.getElementById("solucion")) {
      document.getElementById("solucion").textContent = formatValue(resultData.solucion);
    }

    // Insertar y ejecutar el gráfico de forma limpia
    const plotContainer = document.getElementById("plot-container");
    if (plotContainer) {
      if (resultData.plot_json) {
        // Corrección clave: Controlamos si viene como String o ya parseado
        const ordenGrafico = typeof resultData.plot_json === "string"
          ? JSON.parse(resultData.plot_json)
          : resultData.plot_json;

        // Renderizado nativo e interactivo en el cliente
        Plotly.newPlot('plot-container', ordenGrafico.data, ordenGrafico.layout, { responsive: true });
      } else if (resultData.plot_html) {
        plotContainer.innerHTML = resultData.plot_html;
        executeScriptsInElement(plotContainer);
      } else {
        plotContainer.innerHTML = `<div class="alert alert-warning">No se detectaron matrices de dibujo para la gráfica.</div>`;
      }
    }
  } else {
    // Mostrar mensaje de error si el localStorage está vacío
    const grid = document.querySelector(".content-grid");
    if (grid) {
      grid.innerHTML = `
        <div class="error-container" style="text-align: center; padding: 40px;">
          <h2>No se encontraron resultados</h2>
          <p>Por favor, <a href="/">vuelve al inicio</a> y resuelve un problema primero.</p>
        </div>
      `;
    }
  }
});