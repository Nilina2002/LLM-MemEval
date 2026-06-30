"use client";
import dynamic from "next/dynamic";
import type { PlotlyFigure } from "@/lib/types";

// Plotly is client-only — dynamic import prevents SSR errors
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface DecayCurveProps {
  figure: PlotlyFigure;
  className?: string;
}

export function DecayCurve({ figure, className }: DecayCurveProps) {
  return (
    <div className={className}>
      <Plot
        data={figure.data as Plotly.Data[]}
        layout={{
          ...figure.layout,
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#e2e8f0" },
        } as Plotly.Layout}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: "100%", height: "400px" }}
      />
    </div>
  );
}
