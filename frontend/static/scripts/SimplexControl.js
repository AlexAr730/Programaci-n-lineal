const data = JSON.parse(localStorage.getItem("lp_result"));

const solucion = data.solucion || [];
const valor = data.valor_optimo;
const estado = data.estado;
const historial = data.table_history;
const sensibilidad = data.sensibilidad || {};

// Actualizar resumen
document.getElementById("solucion").textContent = `[${solucion
  .map((x) => x.toFixed(2))
  .join(", ")}]`;
document.getElementById("valor_optimo").textContent =
  valor?.toFixed(2) || "N/A";
document.getElementById("estado").textContent = estado;

// Actualizar análisis de sensibilidad
actualizarSensibilidad(sensibilidad);

function actualizarSensibilidad(sensibilidad) {
  // Precios sombra
  const preciosSombraEl = document.getElementById("precios_sombra");
  if (sensibilidad.precios_sombra && sensibilidad.precios_sombra.length > 0) {
    let preciosHtml = "";
    sensibilidad.precios_sombra.forEach((precio, i) => {
      const valor = parseFloat(precio);
      let className = "price-item";
      if (valor === 0) className += " zero";
      else if (valor > 0) className += " positive";

      preciosHtml += `<span class="${className}">λ${i + 1}: ${valor.toFixed(
        2
      )}</span>`;
    });
    preciosSombraEl.innerHTML = preciosHtml;
  } else {
    preciosSombraEl.innerHTML = '<span class="text-muted">No disponible</span>';
  }

  // Holguras
  const holguras = document.getElementById("holguras");
  if (sensibilidad.holguras && sensibilidad.holguras.length > 0) {
    let holguraHtml = "";
    sensibilidad.holguras.forEach(([nombre, valor]) => {
      const val = parseFloat(valor);
      let className = "slack-item";
      if (val === 0) className += " zero";
      else if (val > 0) className += " positive";

      holguraHtml += `<span class="${className}">${nombre}: ${val.toFixed(
        2
      )}</span>`;
    });
    holguras.innerHTML = holguraHtml;
  } else {
    holguras.innerHTML = '<span class="text-muted">No disponible</span>';
  }
}

// Llenar selector de iteraciones
const selector = document.getElementById("selectorIteracion");
historial.forEach((paso, index) => {
  const option = document.createElement("option");
  option.value = index;
  option.textContent = `Paso ${index + 1}: ${paso.etapa}`;
  selector.appendChild(option);
});

function mostrarIteracion(index) {
  const step = historial[index];
  const table = step.table;
  const basicas = step.basicas;
  const enter = step.enter;
  const sale = step.sale;

  // Información de la iteración
  let infoHtml = `<p><strong>Iteración:</strong> ${step.iteracion}</p>`;
  infoHtml += `<p><strong>Etapa:</strong> ${step.etapa}</p>`;
  if (enter !== null && sale !== null) {
    infoHtml += `<p><strong>Entra:</strong> x${
      enter + 1
    }, <strong>Sale:</strong> x${basicas[sale] + 1}</p>`;
  }
  document.getElementById("iterationInfo").innerHTML = infoHtml;

  // Tabla
  let html = `<table class="table table-bordered table-sm"><thead><tr><th>Variable</th>`;
  for (let j = 0; j < table[0].length - 1; j++) {
    html += `<th>x${j + 1}</th>`;
  }
  html += `<th>RHS</th></tr></thead><tbody>`;

  // Fila objetivo
  html += `<tr><td><strong>Obj (Z)</strong></td>`;
  table[0].forEach((val, j) => {
    let cellClass = enter === j ? "highlight-col" : "";
    html += `<td class="${cellClass}">${val.toFixed(2)}</td>`;
  });
  html += `</tr>`;

  // Restricciones
  for (let i = 1; i < table.length; i++) {
    const varIndex = basicas[i - 1];
    let rowClass = sale === i - 1 ? "highlight-row" : "";

    html += `<tr class="${rowClass}"><td><strong>x${
      varIndex + 1
    }</strong></td>`;
    table[i].forEach((val, j) => {
      let cellClass = "";
      if (enter === j && sale === i - 1) {
        cellClass = "highlight-cell";
      } else if (enter === j) {
        cellClass = "highlight-col";
      } else if (sale === i - 1) {
        cellClass = "highlight-row";
      }
      html += `<td class="${cellClass}">${val.toFixed(2)}</td>`;
    });
    html += `</tr>`;
  }

  html += `</tbody></table>`;
  document.getElementById("tablaIteracion").innerHTML = html;
}

// Mostrar primera iteración por defecto
mostrarIteracion(0);
