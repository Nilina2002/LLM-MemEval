"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import { getConversation } from "@/lib/api";
import { MessageBubble } from "@/components/conversation/MessageBubble";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";

const PAGE_SIZE = 50;

export default function ConversationPage() {
  const { id } = useParams<{ id: string }>();
  const [page, setPage] = useState(1);

  const { data, error } = useSWR(
    id ? `conversation/${id}/${page}` : null,
    () => getConversation(id!, page, PAGE_SIZE)
  );

  if (error) return <div className="text-sm text-red-400 py-8">Failed to load conversation.</div>;
  if (!data) return <LoadingSpinner label="Loading conversation…" />;

  const totalPages = Math.ceil(data.total / PAGE_SIZE);

  if (data.total === 0) {
    return (
      <EmptyState
        title="No messages yet"
        message="Run the experiment to generate the conversation."
        action={
          <Link href={`/experiments/${id}`} className="text-sm text-primary hover:underline">
            ← Back to experiment
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-4 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Conversation</h1>
          <p className="text-muted-foreground text-sm">
            {data.total} messages total · Page {page} of {totalPages}
          </p>
        </div>
        <Link href={`/experiments/${id}`} className="text-sm text-muted-foreground hover:text-foreground">
          ← Experiment
        </Link>
      </div>

      {/* Injected fact legend */}
      <div className="flex items-center gap-2 text-xs text-muted-foreground bg-yellow-400/5 border border-yellow-400/20 rounded-md px-3 py-2">
        <span className="w-2 h-2 rounded-full bg-yellow-400 inline-block" />
        Turns highlighted in yellow contain injected facts
      </div>

      {/* Messages */}
      <div className="space-y-3">
        {data.messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center gap-2 justify-center pt-4">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1.5 rounded-md border text-sm disabled:opacity-40 hover:bg-secondary transition"
          >
            ← Prev
          </button>
          <span className="text-sm text-muted-foreground">
            {page} / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1.5 rounded-md border text-sm disabled:opacity-40 hover:bg-secondary transition"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
