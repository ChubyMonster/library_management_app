import { useEffect, useState } from "react";
import { get } from "../api/client";

import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";

export default function MembersPage() {
  const [members, setMembers] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      const data = await get("/api/users/members");
      setMembers(data);
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Members</h2>
        <Button variant="outline" onClick={load}>Refresh</Button>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Registered members</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Nom</TableHead>
                  <TableHead>Prénom</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Adhésion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((m) => (
                  <TableRow key={m.id_mbre}>
                    <TableCell className="font-medium">{m.id_mbre}</TableCell>
                    <TableCell>{m.nom_mbre}</TableCell>
                    <TableCell>{m.prenom_mbre}</TableCell>
                    <TableCell>{m.email_mbre}</TableCell>
                    <TableCell>{m.date_adhesion || "-"}</TableCell>
                  </TableRow>
                ))}
                {members.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      No members found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
