import { useRef, useState } from "react";
import type { ChangeEvent, DragEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/api/client";
import { Button } from "@/components/ui/button";

const MAX_BYTES = 10 * 1024 * 1024; // 10 MB

export function ImportPage() {
  const navigate = useNavigate();

  // ---- File upload state --------------------------------------------------
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const [uploadBusy, setUploadBusy] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ---- URL import state ---------------------------------------------------
  const [url, setUrl] = useState("");
  const [urlError, setUrlError] = useState<string | null>(null);
  const [urlBusy, setUrlBusy] = useState(false);

  const anyBusy = uploadBusy || urlBusy;

  // ---- Drag-and-drop handlers ---------------------------------------------

  function onDragOver(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
  }

  function onDragEnter(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragOver(true);
  }

  function onDragLeave(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragOver(false);
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) {
      setFile(dropped);
      setFileError(null);
    }
  }

  function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null;
    if (f) {
      setFile(f);
      setFileError(null);
    }
  }

  // ---- Actions ------------------------------------------------------------

  function handleUpload() {
    if (!file) return;
    if (file.size > MAX_BYTES) {
      setFileError("File is too large. Maximum size is 10 MB.");
      return;
    }
    setUploadBusy(true);
    setFileError(null);
    api
      .importFromUpload(file)
      .then((suite) => navigate(`/suites/${suite.id}`))
      .catch((e: unknown) => {
        setFileError(e instanceof Error ? e.message : "Upload failed");
      })
      .finally(() => setUploadBusy(false));
  }

  function handleUrlImport() {
    const trimmed = url.trim();
    if (!trimmed) return;
    setUrlBusy(true);
    setUrlError(null);
    api
      .importFromUrl(trimmed)
      .then((suite) => navigate(`/suites/${suite.id}`))
      .catch((e: unknown) => {
        setUrlError(e instanceof Error ? e.message : "Import failed");
      })
      .finally(() => setUrlBusy(false));
  }

  // ---- Render -------------------------------------------------------------

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Import a Spec</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Upload a Swagger / OpenAPI file or import directly from a URL.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        {/* ---- File upload card ------------------------------------------ */}
        <div className="border border-border rounded-lg p-5 space-y-4">
          <h2 className="font-medium text-sm">Upload file</h2>

          {/* Drop zone */}
          <div
            role="button"
            tabIndex={0}
            aria-label="Click or drag a file here to upload"
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
            onDragOver={onDragOver}
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            className={[
              "flex flex-col items-center justify-center gap-1 rounded-lg",
              "border-2 border-dashed px-4 py-8 cursor-pointer",
              "transition-colors select-none text-sm",
              isDragOver
                ? "border-primary bg-primary/5"
                : "border-border hover:border-primary/50 hover:bg-accent/40",
            ].join(" ")}
          >
            {file ? (
              <>
                <span className="font-medium text-foreground truncate max-w-full px-2 text-center">
                  {file.name}
                </span>
                <span className="text-xs text-muted-foreground">
                  {(file.size / 1024).toFixed(0)} KB · click to change
                </span>
              </>
            ) : (
              <>
                <span className="text-muted-foreground">
                  Drop file here or{" "}
                  <span className="underline text-foreground">browse</span>
                </span>
                <span className="text-xs text-muted-foreground/70">
                  .json · .yaml · .yml · max 10 MB
                </span>
              </>
            )}
          </div>

          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.yaml,.yml"
            className="hidden"
            onChange={onFileChange}
          />

          <Button
            onClick={handleUpload}
            disabled={!file || anyBusy}
            className="w-full"
          >
            {uploadBusy ? "Uploading…" : "Upload"}
          </Button>

          {fileError && (
            <p className="text-sm text-destructive">{fileError}</p>
          )}
        </div>

        {/* ---- URL import card ------------------------------------------- */}
        <div className="border border-border rounded-lg p-5 space-y-4">
          <h2 className="font-medium text-sm">Import from URL</h2>

          <input
            type="url"
            placeholder="https://example.com/openapi.json"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (urlError) setUrlError(null);
            }}
            disabled={anyBusy}
            className={[
              "w-full rounded-md border border-input bg-background",
              "px-3 py-2 text-sm placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-ring",
              "disabled:opacity-50 disabled:cursor-not-allowed",
            ].join(" ")}
          />

          <Button
            onClick={handleUrlImport}
            disabled={!url.trim() || anyBusy}
            className="w-full"
          >
            {urlBusy ? "Importing…" : "Import from URL"}
          </Button>

          {urlError && (
            <p className="text-sm text-destructive">{urlError}</p>
          )}
        </div>
      </div>
    </div>
  );
}
