
// ==========================================
// AQUASENSE AI - COMPLETE FRONTEND JAVASCRIPT
// ==========================================


// ==========================================
// 1. API CONFIGURATION
// ==========================================

const API_BASE_URL = "http://127.0.0.1:8000";

let dashboardSummary = null;
let allAnomalyRecords = [];
let filteredAnomalyRecords = [];


// ==========================================
// 2. PAGE NAVIGATION
// ==========================================

const navButtons = document.querySelectorAll("[data-page]");
const pages = document.querySelectorAll(".page");

const pageTitle = document.getElementById("page-title");

const pageTitles = {
    overview: "Overview",
    prediction: "Demand Prediction",
    anomaly: "Anomaly Detection",
    analytics: "Analytics",
    reports: "Reports"
};

navButtons.forEach((button) => {

    button.addEventListener("click", () => {

        const selectedPage = button.dataset.page;

        navButtons.forEach((nav) => {
            nav.classList.remove("active");
        });

        button.classList.add("active");

        pages.forEach((page) => {

            page.classList.remove("active");

            if (page.id === selectedPage) {
                page.classList.add("active");
            }

        });

        if (pageTitle) {
            pageTitle.textContent =
                pageTitles[selectedPage] || "AquaSense AI";
        }

        if (selectedPage === "overview") {

            setTimeout(() => {
                resizeCharts();
            }, 200);

        }

    });

});


// ==========================================
// 3. FETCH DASHBOARD SUMMARY
// ==========================================

async function fetchDashboardSummary() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/dashboard-summary`
        );

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        dashboardSummary = data;

        console.log("Dashboard Summary:", data);

        updateDashboardMetrics(data);

        createAnomalyChart(data);

        updateAnomalySummary();

    }

    catch (error) {

        console.error(
            "Dashboard Summary Error:",
            error
        );

    }

}


// ==========================================
// 4. UPDATE OVERVIEW KPI CARDS
// ==========================================

function updateDashboardMetrics(data) {

    const metrics = {

        "total-records":
            data.total_records.toLocaleString("en-IN"),

        "total-consumption":
            data.total_consumption.toLocaleString("en-IN"),

        "average-consumption":
            data.average_consumption.toLocaleString("en-IN"),

        "anomaly-alerts":
            data.anomaly_alerts.toLocaleString("en-IN"),

        "normal-records":
            data.normal_records.toLocaleString("en-IN")

    };

    Object.entries(metrics).forEach(([id, value]) => {

        const element = document.getElementById(id);

        if (element) {
            element.textContent = value;
        }

    });

}


// ==========================================
// 5. FETCH ACTUAL CONSUMPTION TRENDS
// ==========================================

async function fetchConsumptionTrends() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/consumption-trends`
        );

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        console.log("Consumption Trends:", data);

        createConsumptionChart(data);

    }

    catch (error) {

        console.error(
            "Consumption Trends Error:",
            error
        );

    }

}


// ==========================================
// 6. ACTUAL CONSUMPTION CHART
// ==========================================

function createConsumptionChart(data) {

    const chartElement =
        document.getElementById("consumption-chart");

    if (!chartElement || !window.Plotly) {
        console.error("Consumption chart element or Plotly not found.");
        return;
    }

    const traces = [

        {
            x: data.months,
            y: data.actual_consumption,
            type: "scatter",
            mode: "lines+markers",
            name: "Actual Consumption",
            line: {
                width: 3
            }
        },

        {
            x: data.months,
            y: data.predicted_consumption,
            type: "scatter",
            mode: "lines+markers",
            name: "Predicted Consumption",
            line: {
                width: 3,
                dash: "dot"
            }
        }

    ];

    const layout = {

        title: {
            text: "Actual vs Predicted Water Consumption",
            font: {
                size: 16
            }
        },

        xaxis: {
            title: {
                text: "Month",
                standoff: 15
            },
            tickangle: -35
        },

        yaxis: {
            title: "Average Consumption"
        },

        paper_bgcolor: "rgba(0,0,0,0)",

        plot_bgcolor: "rgba(0,0,0,0)",

        margin: {
            t: 65,
            l: 60,
            r: 30,
            b: 110
        },

        legend: {
            orientation: "h",
            y: -0.30,
            x: 0.5,
            xanchor: "center"
        },

        autosize: true

    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.react(
        chartElement,
        traces,
        layout,
        config
    );

}


// ==========================================
// 7. ACTUAL ANOMALY DISTRIBUTION CHART
// ==========================================

function createAnomalyChart(data) {

    const chartElement =
        document.getElementById("anomaly-chart");

    if (!chartElement || !window.Plotly) {
        console.error("Anomaly chart element or Plotly not found.");
        return;
    }

    const traces = [

        {
            labels: [
                "Normal Records",
                "Anomaly Alerts"
            ],

            values: [
                data.normal_records,
                data.anomaly_alerts
            ],

            type: "pie",

            hole: 0.65,

            textinfo: "label+percent",

            marker: {
                colors: [
                    "#16a34a",
                    "#ef4444"
                ]
            }

        }

    ];

    const layout = {

        title: {
            text: "Anomaly Distribution",
            font: {
                size: 16
            }
        },

        paper_bgcolor: "rgba(0,0,0,0)",

        plot_bgcolor: "rgba(0,0,0,0)",

        margin: {
            t: 65,
            l: 20,
            r: 20,
            b: 30
        },

        showlegend: false,

        autosize: true

    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.react(
        chartElement,
        traces,
        layout,
        config
    );

}


// ==========================================
// 8. FETCH ANOMALY RECORDS FROM FASTAPI
// ==========================================

async function fetchAnomalyRecords() {

    const tableBody =
        document.getElementById("anomaly-table-body");

    try {

        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">Loading anomaly records...</td>
                </tr>
            `;
        }

        const response = await fetch(
            `${API_BASE_URL}/api/anomaly-records`
        );

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        console.log("Anomaly Records:", data);

        allAnomalyRecords = data.records || [];

        filteredAnomalyRecords = [...allAnomalyRecords];

        updateAnomalySummary();

        displayAnomalyRecords(filteredAnomalyRecords);

        console.log(
            "Total Anomalies:",
            data.total_anomalies
        );

    }

    catch (error) {

        console.error(
            "Anomaly Records Error:",
            error
        );

        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">
                        Unable to load anomaly records.
                        Please check the backend server.
                    </td>
                </tr>
            `;
        }

        const countElement =
            document.getElementById("anomaly-record-count");

        if (countElement) {
            countElement.textContent = "Unable to load records.";
        }

    }

}


// ==========================================
// 9. UPDATE ANOMALY SUMMARY CARDS
// ==========================================

function updateAnomalySummary() {

    const totalAnomalies = allAnomalyRecords.length;

    const totalRecords = dashboardSummary
        ? dashboardSummary.total_records
        : 9173;

    const normalRecords = Math.max(
        0,
        totalRecords - totalAnomalies
    );

    const percentage = totalRecords > 0
        ? (totalAnomalies / totalRecords) * 100
        : 0;

    const anomalyTotal =
        document.getElementById("anomaly-total");

    const anomalyNormal =
        document.getElementById("anomaly-normal");

    const anomalyPercentage =
        document.getElementById("anomaly-percentage");

    if (anomalyTotal) {
        anomalyTotal.textContent =
            totalAnomalies.toLocaleString("en-IN");
    }

    if (anomalyNormal) {
        anomalyNormal.textContent =
            normalRecords.toLocaleString("en-IN");
    }

    if (anomalyPercentage) {
        anomalyPercentage.textContent =
            percentage.toFixed(2) + "%";
    }

}


// ==========================================
// 10. DISPLAY ANOMALY RECORDS IN TABLE
// ==========================================

function displayAnomalyRecords(records) {

    const tableBody =
        document.getElementById("anomaly-table-body");

    const countElement =
        document.getElementById("anomaly-record-count");

    if (!tableBody) {
        return;
    }

    if (records.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    No anomaly records found.
                </td>
            </tr>
        `;

    }

    else {

        tableBody.innerHTML = records.map((record) => {

            const timestamp = escapeHTML(record.timestamp);

            return `
                <tr>

                    <td>${timestamp}</td>

                    <td>
                        ${Number(record.actual_consumption).toLocaleString("en-IN")}
                    </td>

                    <td>
                        ${Number(record.predicted_consumption).toLocaleString("en-IN")}
                    </td>

                    <td>
                        ${Number(record.anomaly_score).toFixed(6)}
                    </td>

                    <td>
                        <span class="anomaly-status">
                            ${escapeHTML(record.status)}
                        </span>
                    </td>

                </tr>
            `;

        }).join("");

    }

    if (countElement) {

        countElement.textContent =
            `Showing ${records.length.toLocaleString("en-IN")} of ${allAnomalyRecords.length.toLocaleString("en-IN")} anomaly records`;

    }

}


// ==========================================
// 11. SAFE HTML TEXT
// ==========================================

function escapeHTML(value) {

    return String(value).replace(/[&<>"']/g, (character) => {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];

    });

}


// ==========================================
// 12. FILTER ANOMALY RECORDS BY DATE
// ==========================================

function filterAnomalyRecords() {

    const startDate =
        document.getElementById("anomaly-start-date").value;

    const endDate =
        document.getElementById("anomaly-end-date").value;

    if (startDate && endDate && startDate > endDate) {

        alert("Start Date cannot be later than End Date.");

        return;

    }

    filteredAnomalyRecords = allAnomalyRecords.filter((record) => {

        const recordDate = record.timestamp.substring(0, 10);

        const afterStart =
            !startDate || recordDate >= startDate;

        const beforeEnd =
            !endDate || recordDate <= endDate;

        return afterStart && beforeEnd;

    });

    displayAnomalyRecords(filteredAnomalyRecords);

}


// ==========================================
// 13. RESET ANOMALY FILTERS
// ==========================================

function resetAnomalyFilters() {

    document.getElementById("anomaly-start-date").value = "";

    document.getElementById("anomaly-end-date").value = "";

    filteredAnomalyRecords = [...allAnomalyRecords];

    displayAnomalyRecords(filteredAnomalyRecords);

}


// ==========================================
// 14. DOWNLOAD ANOMALY RECORDS AS CSV
// ==========================================

function downloadAnomalyCSV() {

    if (filteredAnomalyRecords.length === 0) {

        alert("No anomaly records available to download.");

        return;

    }

    const headers = [
        "Timestamp",
        "Actual Consumption",
        "Predicted Consumption",
        "Anomaly Score",
        "Status"
    ];

    const rows = filteredAnomalyRecords.map((record) => [

        record.timestamp,

        record.actual_consumption,

        record.predicted_consumption,

        record.anomaly_score,

        record.status

    ]);

    const csvContent = [

        headers.join(","),

        ...rows.map((row) =>
            row.map((value) =>
                `"${String(value).replace(/"/g, '""')}"`
            ).join(",")
        )

    ].join("\n");

    const blob = new Blob(
        ["\uFEFF" + csvContent],
        {
            type: "text/csv;charset=utf-8;"
        }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;

    link.download = "AquaSense_Anomaly_Records.csv";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);

}


// ==========================================
// 15. CONNECT FILTER BUTTONS
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    const filterButton =
        document.getElementById("filter-anomalies");

    const resetButton =
        document.getElementById("reset-anomalies");

    const downloadButton =
        document.getElementById("download-anomalies");

    if (filterButton) {

        filterButton.addEventListener(
            "click",
            filterAnomalyRecords
        );

    }

    if (resetButton) {

        resetButton.addEventListener(
            "click",
            resetAnomalyFilters
        );

    }

    if (downloadButton) {

        downloadButton.addEventListener(
            "click",
            downloadAnomalyCSV
        );

    }

});


// ==========================================
// 16. INITIALIZE DASHBOARD
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("AquaSense AI Dashboard Initialized");

    // Load dashboard KPI values
    fetchDashboardSummary();

    // Load monthly consumption trends
    fetchConsumptionTrends();

    // Load actual anomaly records
    fetchAnomalyRecords();

});


// ==========================================
// 17. RESPONSIVE CHART RESIZING
// ==========================================

function resizeCharts() {

    if (!window.Plotly) {
        return;
    }

    const chartIds = [
        "consumption-chart",
        "anomaly-chart"
    ];

    chartIds.forEach((id) => {

        const chart = document.getElementById(id);

        if (chart) {
            Plotly.Plots.resize(chart);
        }

    });

}

window.addEventListener("resize", resizeCharts);




// ==========================================
//  PREDICTION PAGE
// ==========================================

let predictionRecords = [];
let filteredPredictionRecords = [];

// Fetch prediction data from FastAPI
async function loadPredictionData() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/prediction-records`
        );

        if (!response.ok) {
            throw new Error("Unable to load prediction records");
        }

        const data = await response.json();

        predictionRecords = data.records || [];
        filteredPredictionRecords = [...predictionRecords];

        // Update performance cards
        document.getElementById("prediction-total-records").textContent =
            Number(data.total_records).toLocaleString("en-IN");

        document.getElementById("prediction-mae").textContent =
            Number(data.mae).toFixed(2);

        document.getElementById("prediction-average-actual").textContent =
            Number(data.average_actual).toFixed(2);

        document.getElementById("prediction-average-predicted").textContent =
            Number(data.average_predicted).toFixed(2);

        // Display chart and table
        renderPredictionChart(filteredPredictionRecords);
        renderPredictionTable(filteredPredictionRecords);

    } catch (error) {
        console.error("Prediction Error:", error);

        document.getElementById("prediction-record-count").textContent =
            "Unable to load prediction data. Check whether the backend is running.";
    }
}


// ==========================================
//  ACTUAL VS PREDICTED CHART
// ==========================================

function renderPredictionChart(records) {
    const chartElement = document.getElementById("prediction-chart");

    if (!chartElement || typeof Plotly === "undefined") return;

    // Display up to 500 records in chronological order
    const chartRecords = [...records]
        .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
        .slice(-500);

    const timestamps = chartRecords.map(record => record.timestamp);
    const actual = chartRecords.map(record => record.actual_consumption);
    const predicted = chartRecords.map(record => record.predicted_consumption);

    const chartData = [
        {
            x: timestamps,
            y: actual,
            type: "scatter",
            mode: "lines",
            name: "Actual Consumption"
        },
        {
            x: timestamps,
            y: predicted,
            type: "scatter",
            mode: "lines",
            name: "Predicted Consumption"
        }
    ];

    const layout = {
        autosize: true,
        height: 400,
        margin: { t: 30, r: 20, b: 80, l: 65 },
        xaxis: {
            title: "Timestamp",
            automargin: true
        },
        yaxis: {
            title: "Water Consumption",
            automargin: true
        },
        legend: {
            orientation: "h",
            y: -0.25
        }
    };

    Plotly.react(chartElement, chartData, layout, {
        responsive: true
    });
}


// ==========================================
//  PREDICTION RECORDS TABLE
// ==========================================

function renderPredictionTable(records) {
    const tableBody = document.getElementById("prediction-table-body");
    const countElement = document.getElementById("prediction-record-count");

    if (!tableBody || !countElement) return;

    // Show latest 100 records
    const displayedRecords = records.slice(0, 100);

    tableBody.innerHTML = "";

    if (displayedRecords.length === 0) {
        tableBody.innerHTML =
            '<tr><td colspan="4">No prediction records found.</td></tr>';

        countElement.textContent = "No records found.";
        return;
    }

    displayedRecords.forEach(record => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${record.timestamp}</td>
            <td>${Number(record.actual_consumption).toFixed(2)}</td>
            <td>${Number(record.predicted_consumption).toFixed(2)}</td>
            <td>${Number(record.prediction_error).toFixed(2)}</td>
        `;

        tableBody.appendChild(row);
    });

    countElement.textContent =
        `Showing ${displayedRecords.length} of ${records.length} records`;
}


// ==========================================
//  FILTER PREDICTION RECORDS
// ==========================================

document.getElementById("filter-predictions")?.addEventListener("click", () => {
    const startDate = document.getElementById("prediction-start-date").value;
    const endDate = document.getElementById("prediction-end-date").value;

    if (startDate && endDate && startDate > endDate) {
        alert("Start date cannot be later than end date.");
        return;
    }

    filteredPredictionRecords = predictionRecords.filter(record => {
        const recordDate = record.timestamp.substring(0, 10);

        const afterStart = !startDate || recordDate >= startDate;
        const beforeEnd = !endDate || recordDate <= endDate;

        return afterStart && beforeEnd;
    });

    renderPredictionChart(filteredPredictionRecords);
    renderPredictionTable(filteredPredictionRecords);
});


// ==========================================
//  RESET PREDICTION FILTERS
// ==========================================

document.getElementById("reset-predictions")?.addEventListener("click", () => {
    document.getElementById("prediction-start-date").value = "";
    document.getElementById("prediction-end-date").value = "";

    filteredPredictionRecords = [...predictionRecords];

    renderPredictionChart(filteredPredictionRecords);
    renderPredictionTable(filteredPredictionRecords);
});


// ==========================================
//  DOWNLOAD PREDICTION RECORDS AS CSV
// ==========================================

document.getElementById("download-predictions")?.addEventListener("click", () => {
    if (filteredPredictionRecords.length === 0) {
        alert("No prediction records available to download.");
        return;
    }

    const headers = [
        "Timestamp",
        "Actual Consumption",
        "Predicted Consumption",
        "Prediction Error"
    ];

    const rows = filteredPredictionRecords.map(record => [
        record.timestamp,
        record.actual_consumption,
        record.predicted_consumption,
        record.prediction_error
    ]);

    const csvContent = [
        headers.join(","),
        ...rows.map(row => row.join(","))
    ].join("\n");

    const blob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "AquaSense_Prediction_Records.csv";
    link.click();

    URL.revokeObjectURL(url);
});


// Load prediction data
loadPredictionData();


// ==========================================
//  AQUASENSE AI - ANALYTICS PAGE
// ==========================================

async function loadAnalyticsData() {
    try {
        // Fetch data from backend
        const [summaryResponse, trendsResponse, predictionResponse] =
            await Promise.all([
                fetch(`${API_BASE_URL}/api/dashboard-summary`),
                fetch(`${API_BASE_URL}/api/consumption-trends`),
                fetch(`${API_BASE_URL}/api/prediction-records`)
            ]);

        if (!summaryResponse.ok || !trendsResponse.ok || !predictionResponse.ok) {
            throw new Error("Unable to fetch analytics data");
        }

        const summary = await summaryResponse.json();
        const trends = await trendsResponse.json();
        const predictions = await predictionResponse.json();

        // Update analytics summary cards
        document.getElementById("analytics-total-anomalies").textContent =
            Number(summary.anomaly_alerts).toLocaleString("en-IN");

        document.getElementById("analytics-normal-records").textContent =
            Number(summary.normal_records).toLocaleString("en-IN");

        document.getElementById("analytics-mae").textContent =
            Number(predictions.mae).toFixed(2);

        document.getElementById("analytics-average-consumption").textContent =
            Number(summary.average_consumption).toFixed(2);

        // Render charts
        renderAnalyticsMonthlyChart(trends);
        renderAnalyticsAnomalyChart(trends);
        renderAnalyticsErrorChart(predictions.records || []);

    } catch (error) {
        console.error("Analytics Error:", error);
    }
}


// ==========================================
//  MONTHLY CONSUMPTION CHART
// ==========================================

function renderAnalyticsMonthlyChart(data) {
    const chart = document.getElementById("analytics-monthly-chart");

    if (!chart || typeof Plotly === "undefined") return;

    const chartData = [
        {
            x: data.months,
            y: data.actual_consumption,
            type: "bar",
            name: "Actual Consumption"
        },
        {
            x: data.months,
            y: data.predicted_consumption,
            type: "bar",
            name: "Predicted Consumption"
        }
    ];

    const layout = {
        barmode: "group",
        autosize: true,
        height: 400,
        margin: { t: 30, r: 20, b: 80, l: 65 },
        xaxis: {
            title: "Month",
            automargin: true
        },
        yaxis: {
            title: "Average Consumption",
            automargin: true
        },
        legend: {
            orientation: "h",
            y: -0.25
        }
    };

    Plotly.react(chart, chartData, layout, { responsive: true });
}


// ==========================================
//  MONTHLY ANOMALY DISTRIBUTION
// ==========================================

function renderAnalyticsAnomalyChart(data) {
    const chart = document.getElementById("analytics-anomaly-chart");

    if (!chart || typeof Plotly === "undefined") return;

    const chartData = [
        {
            x: data.months,
            y: data.anomaly_counts,
            type: "bar",
            name: "Detected Anomalies"
        }
    ];

    const layout = {
        autosize: true,
        height: 350,
        margin: { t: 30, r: 20, b: 80, l: 65 },
        xaxis: {
            title: "Month",
            automargin: true
        },
        yaxis: {
            title: "Number of Anomalies",
            rangemode: "tozero"
        },
        showlegend: false
    };

    Plotly.react(chart, chartData, layout, { responsive: true });
}


// ==========================================
//  PREDICTION ERROR DISTRIBUTION
// ==========================================

function renderAnalyticsErrorChart(records) {
    const chart = document.getElementById("analytics-error-chart");

    if (!chart || typeof Plotly === "undefined") return;

    const errors = records
        .map(record => Number(record.prediction_error))
        .filter(value => Number.isFinite(value));

    if (errors.length === 0) {
        chart.innerHTML = "<p>No prediction error data available.</p>";
        return;
    }

    const chartData = [
        {
            x: errors,
            type: "histogram",
            nbinsx: 30,
            name: "Prediction Error"
        }
    ];

    const layout = {
        autosize: true,
        height: 350,
        margin: { t: 30, r: 20, b: 65, l: 65 },
        xaxis: {
            title: "Prediction Error",
            zeroline: true
        },
        yaxis: {
            title: "Number of Records",
            rangemode: "tozero"
        },
        showlegend: false
    };

    Plotly.react(chart, chartData, layout, { responsive: true });
}


// ==========================================
//  ANALYTICS CHART RESIZING
// ==========================================

// Resize charts when Analytics navigation is clicked
document.querySelectorAll('[data-page="analytics"]').forEach(button => {
    button.addEventListener("click", () => {
        setTimeout(() => {
            [
                "analytics-monthly-chart",
                "analytics-anomaly-chart",
                "analytics-error-chart"
            ].forEach(id => {
                const chart = document.getElementById(id);

                if (chart && chart.data && typeof Plotly !== "undefined") {
                    Plotly.Plots.resize(chart);
                }
            });
        }, 200);
    });
});


// Load analytics data
loadAnalyticsData();


// ==========================================
//  AQUASENSE AI - REPORT DOWNLOADS
// ==========================================

// Convert data into downloadable CSV

// Convert data into downloadable CSV
function downloadCSV(filename, headers, rows) {

    const escapeCSV = value => {
        const text = String(value ?? "");
        return `"${text.replace(/"/g, '""')}"`;
    };

    const csvContent = [
        headers.map(escapeCSV).join(","),
        ...rows.map(row => row.map(escapeCSV).join(","))
    ].join("\n");

    const blob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);

    // Show download success notification
    showDownloadMessage("Report downloaded successfully!");
}


// ==========================================
//  1. DEMAND PREDICTION REPORT
// ==========================================

document.getElementById("download-prediction-report")
    ?.addEventListener("click", async () => {

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/prediction-records`
            );

            if (!response.ok) {
                throw new Error("Prediction report unavailable");
            }

            const data = await response.json();

            const rows = (data.records || []).map(record => [
                record.timestamp,
                record.actual_consumption,
                record.predicted_consumption,
                record.prediction_error
            ]);

            downloadCSV(
                "AquaSense_Demand_Prediction_Report.csv",
                [
                    "Timestamp",
                    "Actual Consumption",
                    "Predicted Consumption",
                    "Prediction Error"
                ],
                rows
            );

        } catch (error) {
            console.error(error);
            alert("Unable to download prediction report.");
        }
    });


// ==========================================
//  2. ANOMALY DETECTION REPORT
// ==========================================

document.getElementById("download-anomaly-report")
    ?.addEventListener("click", async () => {

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/anomaly-records`
            );

            if (!response.ok) {
                throw new Error("Anomaly report unavailable");
            }

            const data = await response.json();

            const rows = (data.records || []).map(record => [
                record.timestamp,
                record.actual_consumption,
                record.predicted_consumption,
                record.anomaly_score,
                record.status
            ]);

            downloadCSV(
                "AquaSense_Anomaly_Detection_Report.csv",
                [
                    "Timestamp",
                    "Actual Consumption",
                    "Predicted Consumption",
                    "Anomaly Score",
                    "Status"
                ],
                rows
            );

        } catch (error) {
            console.error(error);
            alert("Unable to download anomaly report.");
        }
    });


// ==========================================
//  3. MODEL PERFORMANCE REPORT
// ==========================================

document.getElementById("download-performance-report")
    ?.addEventListener("click", () => {

        const rows = [
            ["Forecasting Model", "Random Forest Regressor"],
            ["Anomaly Detection Model", "Isolation Forest V3"],
            ["Forecasting Training Records", 36691],
            ["Forecasting Testing Records", 9173],
            ["Forecasting Features", 17],
            ["Anomaly Detection Features", 10],
            ["Mean Absolute Error (MAE)", 182.19],
            ["Root Mean Squared Error (RMSE)", 250.99],
            ["R2 Score", 0.949],
            ["Anomaly Detection Threshold", -0.14498929460587992],
            ["Detected Anomalies", 263],
            ["Normal Records", 8910]
        ];

        downloadCSV(
            "AquaSense_Model_Performance_Report.csv",
            ["Metric", "Value"],
            rows
        );
    });


// ==========================================
// REPORT DOWNLOAD SUCCESS NOTIFICATION
// ==========================================

function showDownloadMessage(message) {

    const oldMessage = document.querySelector(".download-toast");

    if (oldMessage) {
        oldMessage.remove();
    }

    const toast = document.createElement("div");

    toast.className = "download-toast";
    toast.textContent = "✓ " + message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
