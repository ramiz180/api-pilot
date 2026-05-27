// Typed API client — hand-written to match backend app/schemas/api.py
// Will switch to OpenAPI generation in a later sprint once types start drifting.

export type Uuid = string;
export type IsoDateTime = string;
export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface EndpointOut {
  id: Uuid;
  method: HttpMethod;
  path: string;
  name: string;
  description: string | null;
}

export interface EndpointDetailOut extends EndpointOut {
  schema: Record<string, unknown>; // matches alias on backend
}

export interface SuiteSummaryOut {
  id: Uuid;
  name: string;
  spec_id: Uuid;
  generation_status: string;
  endpoint_count: number;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
}

export interface SuiteDetailOut {
  id: Uuid;
  name: string;
  spec_id: Uuid;
  generation_status: string;
  endpoints: EndpointOut[];
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
}

// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string, message?: string) {
    super(message ?? `API ${status}: ${detail}`);
    this.status = status;
    this.detail = detail;
  }
}

// ---------------------------------------------------------------------------
// Base request helper
// ---------------------------------------------------------------------------

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${baseUrl}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: unknown };
      detail =
        typeof body.detail === "string"
          ? body.detail
          : JSON.stringify(body.detail);
    } catch {
      // ignore JSON parse failure — keep statusText as detail
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Public API surface
// ---------------------------------------------------------------------------

export const api = {
  async listSuites(): Promise<SuiteSummaryOut[]> {
    return request<SuiteSummaryOut[]>("/api/suites");
  },

  async getSuite(id: Uuid): Promise<SuiteDetailOut> {
    return request<SuiteDetailOut>(`/api/suites/${id}`);
  },

  async importFromUpload(file: File): Promise<SuiteDetailOut> {
    const form = new FormData();
    form.append("file", file);
    // Do NOT set Content-Type — browser sets multipart boundary automatically
    const res = await fetch(`${baseUrl}/api/imports/upload`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = (await res.json()) as { detail?: unknown };
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      } catch {
        // ignore JSON parse failure
      }
      throw new ApiError(res.status, detail);
    }
    return res.json() as Promise<SuiteDetailOut>;
  },

  async importFromUrl(url: string): Promise<SuiteDetailOut> {
    return request<SuiteDetailOut>("/api/imports/url", {
      method: "POST",
      body: JSON.stringify({ url }),
    });
  },
};
