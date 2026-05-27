import type { HttpMethod } from "@/api/client";

const METHOD_COLORS: Record<HttpMethod, string> = {
  GET:    "bg-blue-100   text-blue-800   border-blue-200",
  POST:   "bg-green-100  text-green-800  border-green-200",
  PUT:    "bg-amber-100  text-amber-800  border-amber-200",
  PATCH:  "bg-purple-100 text-purple-800 border-purple-200",
  DELETE: "bg-red-100    text-red-800    border-red-200",
};

export function HttpMethodPill({ method }: { method: HttpMethod }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs font-mono font-semibold border rounded ${METHOD_COLORS[method]}`}
    >
      {method}
    </span>
  );
}
