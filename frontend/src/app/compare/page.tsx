"use client";
// Strategy comparison page

export default function ComparePage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Strategy Comparison</h1>
      <p className="text-muted-foreground">
        Select multiple experiments to compare their memory decay curves side by side.
      </p>
      {/* TODO: experiment multi-select + StrategyComparison chart */}
    </div>
  );
}
