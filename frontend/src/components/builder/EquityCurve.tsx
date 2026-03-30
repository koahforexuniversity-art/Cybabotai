"use client";

import { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface EquityPoint {
  timestamp: string;
  equity: number;
}

interface EquityCurveProps {
  equityCurve: EquityPoint[];
  initialBalance?: number;
  height?: number;
}

export default function EquityCurve({
  equityCurve,
  initialBalance = 10000,
  height = 300,
}: EquityCurveProps) {
  const data = useMemo(() => {
    if (!equityCurve || equityCurve.length === 0) {
      return {
        labels: [],
        datasets: [],
      };
    }

    const labels = equityCurve.map((point) => {
      try {
        const date = new Date(point.timestamp);
        return date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        });
      } catch {
        return point.timestamp;
      }
    });

    const equityValues = equityCurve.map((p) => p.equity);
    const peak = Math.max(...equityValues, initialBalance);

    return {
      labels,
      datasets: [
        {
          label: "Equity",
          data: equityValues,
          borderColor: "#3B82F6",
          backgroundColor: (context: any) => {
            const chart = context.chart;
            const { ctx, chartArea } = chart;
            if (!chartArea) return "rgba(59, 130, 246, 0.1)";

            const gradient = ctx.createLinearGradient(
              0,
              chartArea.top,
              0,
              chartArea.bottom
            );
            gradient.addColorStop(0, "rgba(59, 130, 246, 0.3)");
            gradient.addColorStop(1, "rgba(59, 130, 246, 0.0)");
            return gradient;
          },
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHoverBackgroundColor: "#3B82F6",
          pointHoverBorderColor: "#fff",
          pointHoverBorderWidth: 2,
        },
        {
          label: "Initial Balance",
          data: new Array(equityCurve.length).fill(initialBalance),
          borderColor: "#9CA3AF",
          borderDash: [5, 5],
          borderWidth: 1,
          fill: false,
          pointRadius: 0,
          tension: 0,
        },
      ],
    };
  }, [equityCurve, initialBalance]);

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index" as const,
        intersect: false,
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "rgba(17, 24, 39, 0.95)",
          titleColor: "#F9FAFB",
          bodyColor: "#D1D5DB",
          borderColor: "rgba(255, 255, 255, 0.1)",
          borderWidth: 1,
          padding: 12,
          displayColors: false,
          callbacks: {
            title: (items: any[]) => {
              if (!items.length) return "";
              return items[0].label;
            },
            label: (item: any) => {
              const value = item.parsed.y;
              const pnl = value - initialBalance;
              const pnlPct = ((pnl / initialBalance) * 100).toFixed(2);
              const sign = pnl >= 0 ? "+" : "";
              return [
                `Equity: $${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                `P&L: ${sign}$${pnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${sign}${pnlPct}%)`,
              ];
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: "rgba(156, 163, 175, 0.1)",
            drawBorder: false,
          },
          ticks: {
            color: "#9CA3AF",
            font: {
              size: 11,
            },
            maxTicksLimit: 10,
          },
        },
        y: {
          grid: {
            color: "rgba(156, 163, 175, 0.1)",
            drawBorder: false,
          },
          ticks: {
            color: "#9CA3AF",
            font: {
              size: 11,
            },
            callback: (value: any) =>
              `$${value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
          },
        },
      },
    }),
    [initialBalance]
  );

  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-900 rounded-lg"
        style={{ height: `${height}px` }}
      >
        <p className="text-gray-500">No equity data available</p>
      </div>
    );
  }

  return (
    <div style={{ height: `${height}px` }}>
      <Line data={data} options={options} />
    </div>
  );
}
