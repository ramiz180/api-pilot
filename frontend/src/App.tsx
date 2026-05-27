import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ImportPagePlaceholder } from "./pages/ImportPagePlaceholder";
import { SuiteDetailPagePlaceholder } from "./pages/SuiteDetailPagePlaceholder";
import { SuiteListPage } from "./pages/SuiteListPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<SuiteListPage />} />
          <Route path="/suites/:id" element={<SuiteDetailPagePlaceholder />} />
          <Route path="/import" element={<ImportPagePlaceholder />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
