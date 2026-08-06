document.addEventListener("DOMContentLoaded", () => {

    createMoodChart();

    createDistributionChart();

    createWeeklyChart();

    createMonthlyChart();

});

function getChartData(id){

    const canvas = document.getElementById(id);

    return {

        labels: JSON.parse(canvas.dataset.labels),

        values: JSON.parse(canvas.dataset.values)

    };

}

function createMoodChart(){

    const chart = getChartData("mood-chart");

    new Chart(

        document.getElementById("mood-chart"),

        {

            type: "line",

            data:{

                labels: chart.labels,

                datasets:[{

                    label:"Mood",

                    data: chart.values,

                    borderColor:"#7f5cff",

                    backgroundColor:"rgba(127,92,255,.2)",

                    tension:.4,

                    fill:true,

                    pointRadius:5,

                    pointHoverRadius:8

                }]

            },

            options:{

                responsive:true,

                plugins:{

                    legend:{display:false}

                },

                scales:{

                    y:{

                        min:1,

                        max:8,

                        ticks:{stepSize:1}

                    }

                }

            }

        }

    );

}

function createDistributionChart(){

    const chart = getChartData("distribution-chart");

    new Chart(

        document.getElementById("distribution-chart"),

        {

            type:"doughnut",

            data:{

                labels: chart.labels,

                datasets:[{

                    data: chart.values,

                    backgroundColor:[

                        "#7F5CFF",
                        "#33D17A",
                        "#3D8BFD",
                        "#FF914D",
                        "#F9C74F",
                        "#577590",
                        "#D65DB1",
                        "#6C757D"

                    ]

                }]

            },

            options:{

                responsive:true,

                plugins:{

                    legend:{

                        position:"bottom"

                    }

                }

            }

        }

    );

}

function createWeeklyChart(){

    const chart = getChartData("weekly-chart");

    new Chart(

        document.getElementById("weekly-chart"),

        {

            type:"bar",

            data:{

                labels: chart.labels,

                datasets:[{

                    data: chart.values,

                    backgroundColor:"#33d17a"

                }]

            },

            options:{

                plugins:{

                    legend:{display:false}

                }

            }

        }

    );

}

function createMonthlyChart(){

    const chart = getChartData("monthly-chart");

    new Chart(

        document.getElementById("monthly-chart"),

        {

            type:"line",

            data:{

                labels: chart.labels,

                datasets:[{

                    data: chart.values,

                    borderColor:"#3D8BFD",

                    backgroundColor:"rgba(61,139,253,.2)",

                    tension:.4,

                    fill:true

                }]

            },

            options:{

                plugins:{

                    legend:{display:false}

                }

            }

        }

    );

}