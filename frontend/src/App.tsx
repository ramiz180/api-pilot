import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { fetchHealth, type HealthResponse } from "@/lib/api"

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const checkHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchHealth()
      setHealth(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection failed")
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void checkHealth()
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold">API Pilot</h1>
        <p className="text-gray-400">AI-Native API Testing Workspace</p>

        <div className="p-6 bg-gray-900 rounded-lg border border-gray-800 max-w-md mx-auto">
          <h2 className="text-lg font-semibold mb-4">Backend Status</h2>

          {loading && <p className="text-yellow-400">Connecting…</p>}

          {!loading && error && (
            <div className="text-red-400">
              <p>● Disconnected</p>
              <p className="text-sm mt-1 text-red-300">{error}</p>
            </div>
          )}

          {!loading && health && (
            <div className="text-green-400 space-y-2">
              <p>● Connected</p>
              <pre className="text-left text-sm bg-gray-800 p-3 rounded mt-2 text-gray-300">
                {JSON.stringify(health, null, 2)}
              </pre>
            </div>
          )}

          <Button
            onClick={() => { void checkHealth() }}
            className="mt-4"
            variant="outline"
            disabled={loading}
          >
            {loading ? "Checking…" : "Refresh"}
          </Button>
        </div>

        <p className="text-gray-600 text-sm">Sprint 0 — Foundation Complete</p>
      </div>
    </div>
  )
}

export default App
