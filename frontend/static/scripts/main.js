let constraintCounter = 1;
let selectedMethod = null;

function selectMethod(methodName) {
  selectedMethod = methodName;

  const dropdownButton = document.getElementById("methodDropdown");
  if (dropdownButton) {
    dropdownButton.textContent = methodName;
    dropdownButton.classList.add("method-selected");
  }

  const hiddenMethod = document.getElementById("method");
  if (hiddenMethod) {
    hiddenMethod.value = methodName;
  }

  console.log(hiddenMethod);

  showMessage(`Selected method: ${methodName}`, "success");

  handleMethodSpecificFeatures(methodName);
}

function handleMethodSpecificFeatures(methodName) {
  switch (methodName) {
    case "Graphical Method":
      console.log("Graphical method selected - suitable for 2 variables");
      break;
    case "Simplex Method":
      console.log("Simplex method selected");
      break;
    default:
      console.log("Unknown method selected");
  }
}

function addConstraint() {
  constraintCounter++;
  const constraintsContainer = document.getElementById("constraintsContainer");

  if (!constraintsContainer) {
    console.error("Constraints container not found");
    return;
  }

  const newConstraintGroup = document.createElement("div");
  newConstraintGroup.className = "constraint-group";
  newConstraintGroup.innerHTML = `
    <div class="d-flex align-items-center">
      <input
        type="text"
        class="form-control constraint-input"
        placeholder= "e.g. (1, 0, 4, '<=')"
        aria-label="Constraint ${constraintCounter}"
        name="constraint ${constraintCounter}"
        data-bs-toggle="tooltip"
        data-bs-placement="top"
        title="Enter the constraint in the format: (1, 0, 4, '<=')"
      />
      <button
        type="button"
        class="btn btn-sm btn-remove ms-2"
        onclick="removeConstraint(this)"
        aria-label="Remove constraint"
        title="Remove this constraint"
      >
        ×
      </button>
    </div>
  `;

  constraintsContainer.appendChild(newConstraintGroup);

  const newInput = newConstraintGroup.querySelector(".constraint-input");
  if (newInput) {
    newInput.focus();
  }
}

function removeConstraint(button) {
  const constraintGroup = button.closest(".constraint-group");
  const constraintsContainer = document.getElementById("constraintsContainer");

  if (!constraintGroup || !constraintsContainer) {
    console.error("Could not find constraint elements");
    return;
  }

  if (constraintsContainer.children.length > 1) {
    constraintGroup.remove();
    showMessage("Constraint removed successfully", "success");
  } else {
    showMessage("You must have at least one constraint", "warning");
  }
}

function submitForm() {
  const formData = collectFormData();

  if (!validateFormData(formData)) {
    return;
  }

  sendToBackend(formData);
}

function collectFormData() {
  const objectiveFunction =
    document.getElementById("objectiveFunction")?.value || "";
  const constraints = [];
  const constraintInputs = document.querySelectorAll(".constraint-input");

  constraintInputs.forEach((input, index) => {
    const value = input.value.trim();
    if (value !== "") {
      constraints.push({
        index: index + 1,
        value: value,
      });
    }
  });

  const problemTypeElement = document.querySelector(
    'input[name="problemType"]:checked'
  );
  const problemType = problemTypeElement ? problemTypeElement.value : null;

  return {
    objectiveFunction: objectiveFunction.trim(),
    constraints: constraints,
    problemType: problemType,
    method: selectedMethod,
  };
}

function validateFormData(formData) {
  if (!formData.method) {
    showMessage("Please select a solution method", "error");
    focusElement("methodDropdown");
    return false;
  }

  if (!formData.objectiveFunction) {
    showMessage("Please enter the objective function", "error");
    focusElement("objectiveFunction");
    return false;
  }

  if (formData.constraints.length === 0) {
    showMessage("Please enter at least one constraint", "error");
    focusFirstConstraint();
    return false;
  }

  if (!formData.problemType) {
    showMessage(
      "Please select the problem type (Maximization or Minimization)",
      "error"
    );
    focusElement("checkMax");
    return false;
  }

  if (
    formData.method === "Graphical Method" &&
    formData.constraints.length > 6
  ) {
    showMessage(
      "Graphical method works best with 6 or fewer constraints",
      "warning"
    );
  }

  return true;
}

function processFormData(formData) {
  console.log("=== LINEAR PROGRAMMING FORM DATA ===");
  console.log("Selected Method:", formData.method);
  console.log("Objective Function:", formData.objectiveFunction);
  console.log("Constraints:", formData.constraints);
  console.log("Problem Type:", formData.problemType);
  console.log("Total Constraints:", formData.constraints.length);

  showMessage(
    `Form submitted successfully using ${formData.method}! Check console for details.`,
    "success"
  );
}

function sendToBackend(formData) {
  console.log("Sending form data to backend:", formData);
  fetch("/results", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
      showMessage("Problem solved successfully!", "success");
      localStorage.setItem("lp_result", JSON.stringify(data));

      const redirectUrl =
        formData.method === "Graphical Method"
          ? "/results"
          : formData.method === "Simplex M Method"
          ? "/simplex_results"
          : "/";

      window.location.href = redirectUrl;
    })
    .catch((error) => {
      console.error("Error:", error);
      showMessage("Error processing the problem. Please try again.", "error");
    });
}

function showMessage(message, type) {
  const messageTypes = {
    success: "✅ Success: ",
    error: "❌ Error: ",
    warning: "⚠️ Warning: ",
  };

  alert((messageTypes[type] || "") + message);
}

function focusElement(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.focus();
  }
}

function focusFirstConstraint() {
  const firstConstraint = document.querySelector(".constraint-input");
  if (firstConstraint) {
    firstConstraint.focus();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("keydown", function (event) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      submitForm();
    }

    if ((event.ctrlKey || event.metaKey) && event.key === "+") {
      event.preventDefault();
      addConstraint();
    }
  });

  const objectiveFunctionInput = document.getElementById("objectiveFunction");
  if (objectiveFunctionInput) {
    objectiveFunctionInput.addEventListener("blur", function () {
      if (this.value.trim() === "") {
        this.classList.add("is-invalid");
      } else {
        this.classList.remove("is-invalid");
      }
    });
  }

  initializeConstraintValidation();

  console.log("Linear Programming Form initialized successfully");
});

function initializeConstraintValidation() {
  const constraintsContainer = document.getElementById("constraintsContainer");
  if (!constraintsContainer) return;

  constraintsContainer.addEventListener(
    "blur",
    function (event) {
      if (event.target.classList.contains("constraint-input")) {
        if (event.target.value.trim() === "") {
          event.target.classList.add("is-invalid");
        } else {
          event.target.classList.remove("is-invalid");
        }
      }
    },
    true
  );
}
