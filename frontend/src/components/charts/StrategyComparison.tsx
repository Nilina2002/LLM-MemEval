"use client";
import dynamic from "next/dynamic";
import type { PlotlyFigure } from "@/lib/types";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface StrategyComparisonProps {
  figure: PlotlyFigure;
}

export function StrategyComparison({ figure }: StrategyComparisonProps) {
  return (
    <Plot
      data={figure.data as Plotly.Data[]}
      layout={{
        ...figure.layout,
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: { color: "#e2e8f0" },
      } as Plotly.Layout}
      config={{ responsive: true }}
      style={{ width: "100%", height: "500px" }}
    />
  );
}
