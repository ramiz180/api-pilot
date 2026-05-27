import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type SuiteSummaryOut } from "@/api/client";
import { Button } from "@/components/ui/button";

// ---------------------------------------------------------------------------
// Status badge
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<string, string> = {
  parsed: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  failed: "bg-red-100 text-red-800",
};

function StatusBadge({ status }: { status: string }) {
  const cls =
    STATUS_COLORS[status] ?? "bg-gray-100 text-gray-700";
  return (
    <span
      className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${cls}`}
    >
      {status}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Suite card
// ---------------------------------------------------------------------------

function SuiteCard({ suite }: { suite: SuiteSummaryOut }) {
  return (
    <Link
      to={`/suites/${suite.id}`}
      className="block border border-border rounded-lg p-4 hover:bg-accent transition-colors"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="font-medium text-foreground truncate">{suite.name}</p>
          <p className="text-sm text-muted-foreground mt-0.5">
            {suite.endpoint_count} endpoint
            {suite.endpoint_count !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="shrink-0 flex flex-col items-end gap-1">
          <StatusBadge status={suite.generation_status} />
          <span className="text-xs text-muted-foreground">
            {new Date(suite.created_at).toLocaleString()}
          </span>
        </div>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function SuiteListPage() {
  const [suites, setSuites] = useState<SuiteSummaryOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .listSuites()
      .then((data) => {
        if (!cancelled) setSuites(data);
      })
      .catch((e: unknown) => {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Unknown error");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  };

  useEffect(load, []);

  // --- Loading ---
  if (loading) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-semibold">Suites</h1>
        <p className="text-muted-foreground">Loading…</p>
      </div>
    );
  }

  // --- Error ---
  if (error) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-semibold">Suites</h1>
        <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-4">
          <p className="text-destructive font-medium">Failed to load suites</p>
          <p className="text-sm text-muted-foreground mt-1">{error}</p>
        </div>
        <Button variant="outline" onClick={load}>
          Retry
        </Button>
      </div>
    );
  }

  // --- Empty ---
  if (suites !== null && suites.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">Suites</h1>
        <div className="text-center py-16 border border-dashed border-border rounded-lg">
          <p className="text-muted-foreground text-lg">No suites yet</p>
          <p className="text-muted-foreground text-sm mt-1">
            Import a Swagger / OpenAPI spec to get started.
          </p>
          <Button asChild className="mt-6">
            <Link to="/import">Import your first spec</Link>
          </Button>
        </div>
      </div>
    );
  }

  // --- Success ---
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Suites</h1>
        <Button asChild variant="outline" size="sm">
          <Link to="/import">+ Import</Link>
        </Button>
      </div>
      <div className="space-y-2">
        {(suites ?? []).map((s) => (
          <SuiteCard key={s.id} suite={s} />
        ))}
      </div>
    </div>
  );
}
