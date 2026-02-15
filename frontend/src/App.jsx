import { Routes, Route, Navigate } from "react-router-dom";
import { loadUser } from "./auth/auth";

import Navbar from "./components/Navbar";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import MembersPage from "./pages/MembersPage";
import BooksPage from "./pages/BooksPage";
import LoansPage from "./pages/LoansPage";

function RequireAuth({ children }) {
  const user = loadUser();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<RequireAuth><Dashboard /></RequireAuth>} />
          <Route path="/members" element={<RequireAuth><MembersPage /></RequireAuth>} />
          <Route path="/books" element={<RequireAuth><BooksPage /></RequireAuth>} />
          <Route path="/loans" element={<RequireAuth><LoansPage /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}
