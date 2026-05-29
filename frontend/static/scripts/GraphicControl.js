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

    // Llenar los datos del resumen
    document.getElementById("objetivo").textContent = formatObjective(
      resultData.objetivo
    );
    document.getElementById("valor-optimo").textContent = formatValue(
      resultData.valor_optimo
    );
    document.getElementById("solucion").textContent = formatValue(
      resultData.solucion
    );

    // Insertar y ejecutar el gráfico
    const plotContainer = document.getElementById("plot-container");
    plotContainer.innerHTML = resultData.plot_html;
    executeScriptsInElement(plotContainer);
  } else {
    // Mostrar mensaje de error
    document.querySelector(".content-grid").innerHTML = `
            <div class="error-container">
              <h2> No se encontraron resultados</h2>
              <p>Por favor, <a href="/">vuelve al inicio</a> y resuelve un problema primero.</p>
            </div>
          `;
  }
});
