import { loadUser, isAdmin } from "../auth/auth";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

export default function Dashboard() {
  const user = loadUser();

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <Badge variant="secondary">{user?.login} • {user?.profil?.nom_p}</Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Welcome</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          <p>
            You are connected as <span className="text-foreground font-medium">{user?.login}</span>.
          </p>
          {!isAdmin(user) && (
            <p className="mt-2">
              Note: backend does not enforce admin permissions yet (no JWT middleware). UI is styled for admin workflow.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
