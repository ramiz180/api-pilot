import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError, type SuiteDetailOut } from "@/api/client";
import { Button } from "@/components/ui/button";
import { HttpMethodPill } from "@/components/HttpMethodPill";

// ---------------------------------------------------------------------------
// Status badge (inline — no extra shared component needed yet)
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<string, string> = {
  parsed:  "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  failed:  "bg-red-100 text-red-800",
};

function statusCls(s: string): string {
  return STATUS_COLORS[s] ?? "bg-gray-100 text-gray-700";
}

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------

function LoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-4 bg-muted rounded w-24" />
      <div className="h-8 bg-muted rounded w-1/2 mt-3" />
      <div className="h-4 bg-muted rounded w-1/3" />
      <div className="space-y-2 mt-6">
        {Array.from({ length: 7 }, (_, i) => (
          <div key={i} className="h-14 bg-muted rounded" />
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function SuiteDetailPage() {
  const { id } = useParams();

  const [loading, setLoading] = useState(true);
  const [suite, setSuite] = useState<SuiteDetailOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isNotFound, setIsNotFound] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    if (!id) {
      setIsNotFound(true);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setSuite(null);
    setError(null);
    setIsNotFound(false);

    api
      .getSuite(id)
      .then((data) => {
        if (!cancelled) {
          setSuite(data);
          setLoading(false);
        }
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 404) {
          setIsNotFound(true);
        } else {
          setError(e instanceof Error ? e.message : "Unknown error");
        }
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [id, retryCount]);

  // --- Loading ---
  if (loading) return <LoadingSkeleton />;

  // --- Not found ---
  if (isNotFound) {
    return (
      <div className="space-y-4">
        <Link to="/" className="text-blue-600 hover:underline text-sm">
          ← Back to suites
        </Link>
        <h1 className="text-2xl font-semibold mt-4">Suite not found</h1>
        <p className="text-muted-foreground text-sm">
          This suite doesn't exist or has been deleted.
        </p>
      </div>
    );
  }

  // --- Error ---
  if (error) {
    return (
      <div className="space-y-4">
        <Link to="/" className="text-blue-600 hover:underline text-sm">
          ← Back to suites
        </Link>
        <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-4">
          <p className="text-destructive font-medium">Failed to load suite</p>
          <p className="text-sm text-muted-foreground mt-1">{error}</p>
        </div>
        <Button variant="outline" onClick={() => setRetryCount((c) => c + 1)}>
          Retry
        </Button>
      </div>
    );
  }

  // Guard: should be unreachable if states are set correctly
  if (!suite) return null;

  return (
    <div className="space-y-6">
      {/* ---- Header -------------------------------------------------------- */}
      <div>
        <Link to="/" className="text-blue-600 hover:underline text-sm">
          ← Back to suites
        </Link>

        <div className="flex items-start justify-between gap-4 mt-3">
          <h1 className="text-2xl font-semibold">{suite.name}</h1>
          <span
            className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full mt-1 shrink-0 ${statusCls(suite.generation_status)}`}
          >
            {suite.generation_status}
          </span>
        </div>

        <p className="text-sm text-muted-foreground mt-1">
          {suite.endpoints.length} endpoint
          {suite.endpoints.length !== 1 ? "s" : ""} · Created{" "}
          {new Date(suite.created_at).toLocaleString()}
        </p>
      </div>

      {/* ---- Endpoint list ------------------------------------------------- */}
      <div>
        <h2 className="text-base font-medium mb-3">
          Endpoints ({suite.endpoints.length})
        </h2>

        {suite.endpoints.length === 0 ? (
          <p className="text-muted-foreground text-sm py-10 text-center border border-dashed border-border rounded-lg">
            This suite has no endpoints.
          </p>
        ) : (
          <div className="border border-border rounded-lg divide-y divide-border overflow-hidden">
            {suite.endpoints.map((ep) => (
              <div key={ep.id} className="flex items-start gap-3 px-4 py-3">
                {/* Method pill — fixed-width column */}
                <div className="shrink-0 w-16 mt-0.5">
                  <HttpMethodPill method={ep.method} />
                </div>

                {/* Path + name + description */}
                <div className="min-w-0 flex-1">
                  <code className="font-mono text-sm break-all text-foreground">
                    {ep.path}
                  </code>
                  <div className="flex items-baseline gap-2 mt-0.5">
                    <span className="text-sm font-medium shrink-0">
                      {ep.name}
                    </span>
                    {ep.description && (
                      <span className="text-xs text-muted-foreground truncate">
                        {ep.description}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
