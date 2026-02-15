import { Link, useLocation, useNavigate } from "react-router-dom";
import { clearUser, loadUser } from "../auth/auth";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";

export default function Navbar() {
  const nav = useNavigate();
  const user = loadUser();
  const { pathname } = useLocation();

  const item = (to, label) => (
    <Link
      to={to}
      className={[
        "rounded-md px-3 py-2 text-sm transition",
        pathname === to ? "bg-muted text-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground",
      ].join(" ")}
    >
      {label}
    </Link>
  );

  return (
    <header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-2 px-4 py-3">
        <div className="font-semibold">Library Management</div>

        {user && (
          <nav className="ml-4 flex items-center gap-1">
            {item("/", "Dashboard")}
            {item("/members", "Members")}
            {item("/books", "Books")}
            {item("/loans", "Loans")}
          </nav>
        )}

        <div className="ml-auto flex items-center gap-2">
          {user ? (
            <>
              <Badge variant="secondary">
                {user.login} • {user?.profil?.nom_p}
              </Badge>
              <Button variant="outline" size="sm" onClick={() => { clearUser(); nav("/login"); }}>
                Logout
              </Button>
            </>
          ) : (
            <Button asChild size="sm">
              <Link to="/login">Login</Link>
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
