const chartData = {
    labels: [],
    datasets: [
        {
            label: 'Temperature',
            data: [],
            borderColor: '#F66151',
            backgroundColor: '#F6615150',
            borderWidth: 2,
        },
        {
            label: 'Pressure',
            data: [],
            borderColor: '#F8E45C',
            backgroundColor: '#F8E45C50',
            borderWidth: 2,
        },
        {
            label: 'Humidity',
            data: [],
            borderColor: '#62A0EA',
            backgroundColor: '#62A0EA50',
            color: 'green',
            borderWidth: 2,
        }
    ]
};

let intervalId = null;
const ctx = document.getElementById('chartCanvas').getContext('2d');
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
                        size: 14,
                        family: 'Arial'
                    },
                    color: '#9E9E9E',
                    usePointStyle: true
                }
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
                        family: 'Arial'
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
                        family: 'Arial'
                    },
                    color: '#9E9E9E'
                }
            }
        }
    }
});

function createLinks() {
    var s = document.querySelectorAll('span[data-href]');
    for (var i = 0; i < s.length; i++) {
        var s = s[i];
        s.addEventListener('click', function (e) {
            var t = e.target;
            window.location.replace(t.getAttribute('data-href'));
        });
    }
}

function setupSidebarLogic() {
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    const pages = document.querySelectorAll('.page');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const targetPageId = link.getAttribute('data-href').substring(1);
            pages.forEach(page => {
                if (page.id === targetPageId) {
                    page.classList.add('active');
                    // link.classList.add('active');
                } else {
                    page.classList.remove('active');
                    // link.classList.remove('active');
                }
            });
            sidebarLinks.forEach(l => {
                if (l.getAttribute('data-href').substring(1) === targetPageId) {
                    l.classList.add('active');
                } else {
                    l.classList.remove('active');
                }
            });
        });
    });
}

function saveSettings() {
    const hostName = document.getElementById("settingsHostName");
    localStorage.setItem("hostName", hostName.value);

    const portNumber = document.getElementById("settingsPortNumber");
    localStorage.setItem("portNumber", portNumber.value);

    const refreshTime = document.getElementById("settingsRefreshTime");
    localStorage.setItem("refreshTime", refreshTime.value);
}

function restoreSettings() {
    const hostName = document.getElementById("settingsHostName");
    const hostNamePref = localStorage.getItem("hostName");
    if (hostNamePref && hostName) {
        hostName.value = hostNamePref;
    }

    const portNumber = document.getElementById("settingsPortNumber");
    const portNumberPref = localStorage.getItem("portNumber");
    if (portNumberPref && portNumber) {
        portNumber.value = portNumberPref;
    }

    const refreshTime = document.getElementById("settingsRefreshTime");
    const refreshTimePref = localStorage.getItem("refreshTime");
    if (refreshTimePref && refreshTime) {
        refreshTime.value = refreshTimePref;
    }
}

function rgbToHex(r, g, b) {
    return "#" + (1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1);
}

function getLedGrid() {
    const apiEndpoint = 'http://127.0.0.1:8000/leds/get/all';
    fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('ledGrid');
            container.innerHTML = '';

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

        // Use a gray color if the LED is off
        if (colorArray === [100, 100, 100]) {
            colorArray = [0, 0, 0];
        }

        colors.push(colorArray);
    }

    const colorsJSON = JSON.stringify(colors);
    const apiEndpoint = 'http://127.0.0.1:8000/leds/set/all?arr=' + colorsJSON;
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
    const apiEndpoint = 'http://127.0.0.1:8000/leds/set/all?arr=' + colorsJSON;
    fetch(apiEndpoint, {
        method: "POST",
        body: colorsJSON,
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });

    getLedGrid();
}

function startUpdating() {
    intervalId = setInterval(updateChartData, 1000);
}

function stopUpdating() {
    clearInterval(intervalId);
}

function updateChartData() {
    fetch('http://127.0.0.1:8000/sensors/all?t=c&p=hpa&h=perc')
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

window.onload = function () {
    restoreSettings();
    var settingsSaveButton = document.getElementById("settingsSaveButton");
    settingsSaveButton.addEventListener("click", saveSettings, false);

    createLinks();
    setupSidebarLogic();

    startUpdating();

    getLedGrid();
    var ledRefreshButton = document.getElementById("ledRefreshButton");
    ledRefreshButton.addEventListener("click", getLedGrid, false);
    var ledClearButton = document.getElementById("ledClearButton");
    ledClearButton.addEventListener("click", resetLedGrid, false);
    var ledApplyButton = document.getElementById("ledApplyButton");
    ledApplyButton.addEventListener("click", setLedGrid, false);
};
