"use client";

import { useMemo } from "react";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Radar } from "react-chartjs-2";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface RadarChartProps {
  profitability: number;
  riskManagement: number;
  consistency: number;
  robustness: number;
  efficiency: number;
  stability: number;
  height?: number;
}

export default function RadarChart({
  profitability,
  riskManagement,
  consistency,
  robustness,
  efficiency,
  stability,
  height = 300,
}: RadarChartProps) {
  const data = useMemo(
    () => ({
      labels: [
        "Profitability",
        "Risk Management",
        "Consistency",
        "Robustness",
        "Efficiency",
        "Stability",
      ],
      datasets: [
        {
          label: "Strategy Score",
          data: [profitability, riskManagement, consistency, robustness, efficiency, stability],
          backgroundColor: "rgba(59, 130, 246, 0.2)",
          borderColor: "rgba(59, 130, 246, 1)",
          borderWidth: 2,
          pointBackgroundColor: "rgba(59, 130, 246, 1)",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "rgba(59, 130, 246, 1)",
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    }),
    [profitability, riskManagement, consistency, robustness, efficiency, stability]
  );

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: {
            stepSize: 20,
            color: "#9CA3AF",
            backdropColor: "transparent",
            font: {
              size: 10,
            },
          },
          grid: {
            color: "rgba(156, 163, 175, 0.2)",
          },
          angleLines: {
            color: "rgba(156, 163, 175, 0.2)",
          },
          pointLabels: {
            color: "#F9FAFB",
            font: {
              size: 11,
              weight: 500 as const,
            },
          },
        },
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
            label: (item: any) => {
              return `Score: ${item.parsed.r}/100`;
            },
          },
        },
      },
    }),
    []
  );

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-blue-400";
    if (score >= 40) return "text-yellow-400";
    return "text-red-400";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Fair";
    return "Poor";
  };

  const overallScore = useMemo(() => {
    return (
      (profitability + riskManagement + consistency + robustness + efficiency + stability) /
      6
    );
  }, [profitability, riskManagement, consistency, robustness, efficiency, stability]);

  return (
    <div className="space-y-4">
      <div style={{ height: `${height}px` }}>
        <Radar data={data} options={options} />
      </div>

      {/* Score breakdown */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Overall Score</span>
          <span className={`font-semibold ${getScoreColor(overallScore)}`}>
            {overallScore.toFixed(0)}/100 — {getScoreLabel(overallScore)}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <ScoreItem label="Profitability" score={profitability} />
          <ScoreItem label="Risk Management" score={riskManagement} />
          <ScoreItem label="Consistency" score={consistency} />
          <ScoreItem label="Robustness" score={robustness} />
          <ScoreItem label="Efficiency" score={efficiency} />
          <ScoreItem label="Stability" score={stability} />
        </div>
      </div>
    </div>
  );
}

function ScoreItem({ label, score }: { label: string; score: number }) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-emerald-500";
    if (score >= 60) return "bg-blue-500";
    if (score >= 40) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-300 font-medium">{score.toFixed(0)}</span>
      </div>
      <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${getScoreColor(score)} transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}
