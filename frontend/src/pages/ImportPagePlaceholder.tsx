import { Link } from "react-router-dom";

export function ImportPagePlaceholder() {
  return (
    <div className="p-6">
      <Link to="/" className="text-blue-600 hover:underline">
        ← Back to suites
      </Link>
      <h1 className="text-2xl font-semibold mt-4">
        Import (coming in 1d-ii)
      </h1>
    </div>
  );
}
