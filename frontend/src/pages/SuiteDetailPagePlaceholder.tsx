import { Link, useParams } from "react-router-dom";

export function SuiteDetailPagePlaceholder() {
  const { id } = useParams();
  return (
    <div className="p-6">
      <Link to="/" className="text-blue-600 hover:underline">
        ← Back to suites
      </Link>
      <h1 className="text-2xl font-semibold mt-4">
        Suite detail (coming in 1d-ii)
      </h1>
      <p className="text-muted-foreground mt-2">
        Suite ID: <code className="font-mono text-sm">{id}</code>
      </p>
    </div>
  );
}
