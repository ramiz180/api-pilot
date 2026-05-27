import { NavLink, Outlet } from "react-router-dom";

function navClass({ isActive }: { isActive: boolean }) {
  return [
    "text-sm font-medium px-3 py-1.5 rounded-md transition-colors",
    isActive
      ? "bg-primary text-primary-foreground"
      : "text-muted-foreground hover:text-foreground hover:bg-accent",
  ].join(" ");
}

export function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav bar */}
      <header className="border-b border-border bg-card">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="font-semibold text-foreground">API Pilot</span>
          <nav className="flex items-center gap-1">
            <NavLink to="/" end className={navClass}>
              Suites
            </NavLink>
            <NavLink to="/import" className={navClass}>
              Import
            </NavLink>
          </nav>
        </div>
      </header>

      {/* Page content */}
      <main className="flex-1">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
