document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");
    const themeStyle = document.getElementById("theme-style");
    const imageInput = document.getElementById("imageInput");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const preview = document.getElementById("preview");
    const resultCard = document.getElementById("result-card");
    const resultDiv = document.getElementById("result");
    const errorDiv = document.getElementById("error");

    // Theme toggle logic
    function setTheme(theme) {
        if (theme === "dark") {
            themeStyle.href = "/static/css/theme-dark.css";
            themeToggle.textContent = "☀️";
        } else {
            themeStyle.href = "/static/css/theme-light.css";
            themeToggle.textContent = "🌙";
        }
        localStorage.setItem("theme", theme);
    }
    themeToggle.addEventListener("click", () => {
        const current = localStorage.getItem("theme") || "light";
        setTheme(current === "light" ? "dark" : "light");
    });
    setTheme(localStorage.getItem("theme") || "light");

    // Image preview
    imageInput.addEventListener("change", function () {
        preview.innerHTML = "";
        errorDiv.textContent = "";
        resultCard.style.display = "none";
        const file = this.files[0];
        if (file) {
            const img = document.createElement("img");
            img.src = URL.createObjectURL(file);
            img.onload = () => URL.revokeObjectURL(img.src);
            preview.appendChild(img);
        }
    });

    // Move the event listener registration inside DOMContentLoaded
    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", async function () {
            errorDiv.textContent = "";
            resultCard.style.display = "none";
           // resultDiv.textContent = "";
            const file = imageInput.files[0];
            if (!file) {
                errorDiv.textContent = "Please select an image.";
                return;
            }
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = "Analyzing...";
            try {
                // Read file as base64 and send as JSON
                const reader = new FileReader();
                reader.onload = async function (e) {
                    const base64Data = e.target.result;
                    const extension = file.name.split('.').pop().toLowerCase();
                    const res = await fetch("/upload/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            image_data: base64Data,
                            extension: extension
                        })
                    });
                    const data = await res.json();
                    if (data.error) {
                        errorDiv.textContent = data.error;
                    } else {
                        resultCard.style.display = "block";
                        // Inject results into result-table-body
                        const tableBody = document.getElementById("result-table-body");
                        if (tableBody) {
                            tableBody.innerHTML = "";
                            const foods = Array.isArray(data.foods) ? data.foods : [];
                            const calories = Array.isArray(data.calories) ? data.calories : [];
                            const portions = Array.isArray(data.portions) ? data.portions : [];
                            let totalCalories = 0;
                            for (let i = 0; i < foods.length; i++) {
                                const tr = document.createElement("tr");
                                const tdFood = document.createElement("td");
                                tdFood.textContent = foods[i] || "-";
                                const tdCal = document.createElement("td");
                                tdCal.textContent = calories[i] !== undefined ? calories[i] : "-";
                                const tdPortion = document.createElement("td");
                                tdPortion.textContent = portions[i] || "-";
                                tr.appendChild(tdFood);
                                tr.appendChild(tdCal);
                                tr.appendChild(tdPortion);
                                tableBody.appendChild(tr);
                                // Sum calories if it's a number
                                const calVal = parseFloat(calories[i]);
                                if (!isNaN(calVal)) {
                                    totalCalories += calVal;
                                }
                            }
                            // Add total calories row
                            if (foods.length > 0) {
                                const totalTr = document.createElement("tr");
                                const tdLabel = document.createElement("td");
                                tdLabel.textContent = "Total Calories";
                                tdLabel.colSpan = 1;
                                tdLabel.style.fontWeight = "bold";
                                const tdTotal = document.createElement("td");
                                tdTotal.textContent = totalCalories;
                                tdTotal.style.fontWeight = "bold";
                                const tdEmpty = document.createElement("td");
                                totalTr.appendChild(tdLabel);
                                totalTr.appendChild(tdTotal);
                                totalTr.appendChild(tdEmpty);
                                tableBody.appendChild(totalTr);
                            }
                        }                      
                    }
                    analyzeBtn.disabled = false;
                    analyzeBtn.textContent = "Analyze";
                };
                reader.readAsDataURL(file);
            } catch (e) {
                errorDiv.textContent = "An error occurred. Please try again.";
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = "Analyze";
            }
        });
    }
});
