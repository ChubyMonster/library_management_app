import { useEffect, useState } from "react";
import { get, post } from "../api/client";

import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";

export default function LoansPage() {
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loans, setLoans] = useState([]);
  const [error, setError] = useState("");

  const [bookId, setBookId] = useState("");
  const [memberId, setMemberId] = useState("");
  const [dateEmprunt, setDateEmprunt] = useState("2026-02-13");

  async function loadAll() {
    setError("");
    try {
      const [b, m, l] = await Promise.all([
        get("/api/books/books"),
        get("/api/users/members"),
        get("/api/loans/"),
      ]);
      setBooks(b);
      setMembers(m);
      setLoans(l);

      if (!bookId && b[0]) setBookId(String(b[0].id_livre));
      if (!memberId && m[0]) setMemberId(String(m[0].id_mbre));
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function createLoan() {
    setError("");
    try {
      await post("/api/loans/", {
        livre_id: Number(bookId),
        membre_id: Number(memberId),
        date_emprunt: dateEmprunt,
      });
      await loadAll();
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  async function returnLoan(id) {
    setError("");
    try {
      const today = new Date().toISOString().slice(0, 10);
      await post(`/api/loans/${id}/return`, { date_retour: today });
      await loadAll();
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Loans</h2>
        <Button variant="outline" onClick={loadAll}>Refresh</Button>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <Card>
        <CardHeader><CardTitle>Create loan</CardTitle></CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="grid gap-2">
            <Label>Book</Label>
            <Select value={bookId} onValueChange={setBookId}>
              <SelectTrigger><SelectValue placeholder="Choose book" /></SelectTrigger>
              <SelectContent>
                {books.map((b) => (
                  <SelectItem key={b.id_livre} value={String(b.id_livre)}>
                    #{b.id_livre} — {b.titre} (qte: {b.quantite})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2">
            <Label>Member</Label>
            <Select value={memberId} onValueChange={setMemberId}>
              <SelectTrigger><SelectValue placeholder="Choose member" /></SelectTrigger>
              <SelectContent>
                {members.map((m) => (
                  <SelectItem key={m.id_mbre} value={String(m.id_mbre)}>
                    #{m.id_mbre} — {m.nom_mbre} {m.prenom_mbre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2">
            <Label>Date emprunt</Label>
            <Input value={dateEmprunt} onChange={(e) => setDateEmprunt(e.target.value)} placeholder="YYYY-MM-DD" />
          </div>

          <div className="md:col-span-3">
            <Button onClick={createLoan}>Borrow</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Loans list</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Book</TableHead>
                  <TableHead>Member</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Returned</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loans.map((l) => (
                  <TableRow key={l.id_emprunt}>
                    <TableCell className="font-medium">{l.id_emprunt}</TableCell>
                    <TableCell>{l.livre ? `${l.livre.titre} (#${l.livre.id_livre})` : `#${l.livre_id}`}</TableCell>
                    <TableCell>{l.membre ? `${l.membre.nom_mbre} ${l.membre.prenom_mbre}` : `#${l.membre_id}`}</TableCell>
                    <TableCell>{l.date_emprunt}</TableCell>
                    <TableCell>{l.date_retour || "-"}</TableCell>
                    <TableCell>
                      {!l.date_retour ? (
                        <Button size="sm" onClick={() => returnLoan(l.id_emprunt)}>Return</Button>
                      ) : (
                        <span className="text-sm text-muted-foreground">Done</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {loans.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      No loans found.
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
