// Global ID of the timer
let intervalId = null;

let hostNamePref = localStorage.getItem("hostName") || "localhost";
let portNumberPref = localStorage.getItem("portNumber") || "8000";
let refreshTimePref = localStorage.getItem("refreshTime") || 1000;
let activePagePref = localStorage.getItem("activePage") || 0;

const chartData = {
    labels: [],
    datasets: [
        {
            label: 'Temperature [°C]  ',
            data: [],
            borderColor: '#F66151',
            backgroundColor: '#F6615150',
            borderWidth: 2,
        },
        {
            label: 'Pressure [hPa]  ',
            data: [],
            borderColor: '#F8E45C',
            backgroundColor: '#F8E45C50',
            borderWidth: 2,
        },
        {
            label: 'Humidity [%]  ',
            data: [],
            borderColor: '#62A0EA',
            backgroundColor: '#62A0EA50',
            color: 'green',
            borderWidth: 2,
        }
    ]
};

const ctx = document.getElementById("chartCanvas").getContext("2d");
const chart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 16,
                    },
                    color: '#F2F2F2',
                    usePointStyle: true
                },
                position: "bottom",
                align: "center"
            }
        },
        scales: {
            y: {
                grid: {
                    color: 'rgba(200, 200, 200, 0.2)'
                },
                ticks: {
                    font: {
                        size: 14,
                    },
                    color: '#9E9E9E'
                }
            },
            x: {
                grid: {
                    color: 'rgba(200, 200, 200, 0.2)'
                },
                ticks: {
                    font: {
                        size: 14,
                    },
                    color: '#9E9E9E'
                }
            }
        }
    }
});

function updateAll() {
    updateSensorsData();
    updateSensorsPlot();
}

function startTimer() {
    if (intervalId) {
        clearInterval(intervalId);
    }

    intervalId = setInterval(updateAll, refreshTimePref);
}

function createLinks() {
    var s = document.querySelectorAll("span[data-href]");
    for (var i = 0; i < s.length; i++) {
        var s = s[i];
        s.addEventListener("click", function (e) {
            var t = e.target;
            window.location.replace(t.getAttribute("data-href"));
        });
    }
}

function setupSidebarLogic() {
    const sidebarLinks = document.querySelectorAll(".sidebar-link");
    const pages = document.querySelectorAll(".page");

    // Restore active page
    sidebarLinks[activePagePref].classList.add("active");
    pages[activePagePref].classList.add("active");

    sidebarLinks.forEach(link => {
        link.addEventListener("click", e => {
            e.preventDefault();
            const targetPageId = link.getAttribute("data-href").substring(1);
            pages.forEach(page => {
                if (page.id === targetPageId) {
                    page.classList.add("active");
                    const id = targetPageId.replace("page", "");
                    localStorage.setItem("activePage", id - 1);
                } else {
                    page.classList.remove("active");
                }
            });
            sidebarLinks.forEach(l => {
                if (l.getAttribute("data-href").substring(1) === targetPageId) {
                    l.classList.add("active");
                } else {
                    l.classList.remove("active");
                }
            });
        });
    });
}

function saveSettings() {
    const hostName = document.getElementById("settingsHostName");
    localStorage.setItem("hostName", hostName.value);
    hostNamePref = hostName.value || "localhost";

    const portNumber = document.getElementById("settingsPortNumber");
    localStorage.setItem("portNumber", portNumber.value);
    portNumberPref = portNumber.value || "8000";

    const refreshTime = document.getElementById("settingsRefreshTime");
    localStorage.getItem("activePage")
    refreshTimePref = refreshTime.value || 1000;

    startTimer();
}

function restoreSettings() {
    const hostName = document.getElementById("settingsHostName");
    if (hostNamePref) {
        hostName.value = hostNamePref;
    }

    const portNumber = document.getElementById("settingsPortNumber");
    if (portNumberPref) {
        portNumber.value = portNumberPref;
    }

    const refreshTime = document.getElementById("settingsRefreshTime");
    if (refreshTimePref) {
        refreshTime.value = refreshTimePref;
    }
}

function rgbToHex(r, g, b) {
    return "#" + (1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1);
}

function updateSensorsData() {
    const apiEndpoint = "http://" + hostNamePref + ":" + portNumberPref + "/sensors/all?t=c&p=hpa&h=perc&ro=deg&pi=deg&ya=deg";
    const sensorsContainer = document.getElementById("sensorsTable");

    fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => {
            // Create the table header
            sensorsContainer.innerHTML = "";
            const header = sensorsContainer.createTHead();
            header.setAttribute("id", "sensorsTableHeader");
            const row = header.insertRow();
            const nameHeader = row.insertCell();
            const valueHeader = row.insertCell();
            const unitHeader = row.insertCell();
            nameHeader.innerText = "Name";
            valueHeader.innerText = "Value";
            unitHeader.innerText = "Unit";

            const body = sensorsContainer.createTBody();
            for (const key in data) {
                const row = body.insertRow();
                const nameCell = row.insertCell();
                const valueCell = row.insertCell();
                const unitCell = row.insertCell();
                nameCell.innerText = data[key].name || key;
                valueCell.innerText = Math.round(data[key].value * 100) / 100 || "0";
                unitCell.innerText = data[key].unit || "-";
            }
        })
        .catch(error => console.log(error));
}

function updateSensorsPlot() {
    const apiEndpoint = "http://" + hostNamePref + ":" + portNumberPref + "/sensors/all?t=c&p=hpa&h=perc";

    fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => {
            chartData.labels.push(new Date().toLocaleTimeString());
            chartData.datasets[0].data.push(data.temperature.value);
            chartData.datasets[1].data.push(data.pressure.value);
            chartData.datasets[2].data.push(data.humidity.value);

            // Limit chart data points
            if (chartData.labels.length > 10) {
                chartData.labels.shift();
                chartData.datasets[0].data.shift();
                chartData.datasets[1].data.shift();
                chartData.datasets[2].data.shift();
            }

            chart.update();
        })
        .catch(error => console.error(error));
}

function updateLedGrid() {
    const apiEndpoint = "http://" + hostNamePref + ":" + portNumberPref + "/leds/get/all";

    fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("ledGrid");
            container.innerHTML = "";

            let id = 0
            data.forEach((color) => {
                let hexColor = rgbToHex(color[0], color[1], color[2]);
                if (hexColor == "#000000") {
                    hexColor = "#787878"
                }

                const input = document.createElement("input");
                input.type = "color";
                input.id = id++;
                input.classList.add("grid-item");

                input.value = hexColor;

                container.appendChild(input);
            });
        })
        .catch(error => console.error(error));
}

function setLedGrid() {
    let colors = [];
    const colorInputs = document.querySelectorAll('input[type="color"]');
    for (let i = 0; i < colorInputs.length; i++) {
        const colorValue = colorInputs[i].value;
        let colorArray = [
            parseInt(colorValue.substring(1, 3), 16),
            parseInt(colorValue.substring(3, 5), 16),
            parseInt(colorValue.substring(5, 7), 16),
        ];

        // Use a gray color if an LED is off
        if (colorArray.toString() == [120, 120, 120].toString()) {
            colorArray = [0, 0, 0];
        }

        colors.push(colorArray);
    }

    const colorsJSON = JSON.stringify(colors);
    const apiEndpoint = "http://" + hostNamePref + ":" + portNumberPref + "/leds/set/all?arr=" + colorsJSON;

    fetch(apiEndpoint, {
        method: "POST",
        body: colorsJSON,
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
}

function resetLedGrid() {
    let colors = [];
    const colorInputs = document.querySelectorAll('input[type="color"]');
    for (let i = 0; i < colorInputs.length; i++) {
        let colorArray = [0, 0, 0];
        colors.push(colorArray);
    }

    const colorsJSON = JSON.stringify(colors);
    const apiEndpoint = "http://" + hostNamePref + ":" + portNumberPref + "/leds/set/all?arr=" + colorsJSON;

    fetch(apiEndpoint, {
        method: "POST",
        body: colorsJSON,
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });

    updateLedGrid();
}

window.onload = function () {
    restoreSettings();
    createLinks();
    setupSidebarLogic();
    updateAll();
    updateLedGrid();
    startTimer();

    var ledRefreshButton = document.getElementById("ledRefreshButton");
    ledRefreshButton.addEventListener("click", updateLedGrid, false);
    var ledClearButton = document.getElementById("ledClearButton");
    ledClearButton.addEventListener("click", resetLedGrid, false);
    var ledApplyButton = document.getElementById("ledApplyButton");
    ledApplyButton.addEventListener("click", setLedGrid, false);

    var settingsSaveButton = document.getElementById("settingsSaveButton");
    settingsSaveButton.addEventListener("click", saveSettings, false);
};
