export function LoadingSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-muted-foreground py-8">
      <div className="w-4 h-4 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
