export default function configs(labels = [], datasets = []) {
  if (!datasets.length || !datasets[0].data || !datasets[0].backgroundColor) {
    return {
      data: {
        labels: [],
        datasets: [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  }

  const maxAccounts = 10;

  const sortedData = datasets[0].data
    .map((val, i) => ({
      label: labels[i],
      value: val,
      color: datasets[0].backgroundColor[i] || "#9e9e9e",
    }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, maxAccounts);

  const filteredLabels = sortedData.map((d) => d.label);
  const filteredData = sortedData.map((d) => d.value);
  const filteredColors = sortedData.map((d) => d.color);

  return {
    data: {
      labels: filteredLabels,
      datasets: [
        {
          label: datasets[0].label || "PnL",
          data: filteredData,
          backgroundColor: filteredColors,
          borderRadius: 6,
          barThickness: 20,
          maxBarThickness: 25,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: "rgba(255, 255, 255, 0.08)",
            borderDash: [3, 3],
          },
          ticks: {
            color: "rgba(255, 255, 255, 0.7)", // soft white
            font: {
              size: 14,
              weight: "600",
              family: "Roboto, sans-serif",
            },
            padding: 10,
            callback: (value) => `$${value}`,
          },
        },
        x: {
          grid: {
            display: false,
          },
          ticks: {
            color: "rgba(255, 255, 255, 0.7)", // soft white
            font: {
              size: 14,
              weight: "600",
              family: "Roboto, sans-serif",
            },
            padding: 8,
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "#1e1e1e",
          titleColor: "#fff",
          bodyColor: "#fff",
          callbacks: {
            label: function (context) {
              const value = context.raw;
              return `${context.label}: $${value.toFixed(2)}`;
            },
          },
        },
      },
    },
  };
}
