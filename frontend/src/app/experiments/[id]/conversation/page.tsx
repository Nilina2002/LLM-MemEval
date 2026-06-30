"use client";
import { useParams } from "next/navigation";

export default function ConversationPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Conversation Viewer</h1>
      <p className="text-muted-foreground">Experiment: {id}</p>
      {/* TODO: ConversationViewer component — paginated message list */}
    </div>
  );
}
