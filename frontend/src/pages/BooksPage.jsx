import { useEffect, useState } from "react";
import { get, post } from "../api/client";

import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";

export default function BooksPage() {
  const [categories, setCategories] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [books, setBooks] = useState([]);
  const [error, setError] = useState("");

  // forms
  const [catName, setCatName] = useState("Informatique");
  const [catChamp, setCatChamp] = useState("Tech");

  const [aNom, setANom] = useState("Martin");
  const [aPrenom, setAPrenom] = useState("Robert");

  const [titre, setTitre] = useState("Clean Code");
  const [isbn, setIsbn] = useState("9780132350884");
  const [quantite, setQuantite] = useState(3);
  const [catId, setCatId] = useState("");
  const [authorId, setAuthorId] = useState("");

  async function loadAll() {
    setError("");
    try {
      const [c, a, b] = await Promise.all([
        get("/api/books/categories"),
        get("/api/books/authors"),
        get("/api/books/books"),
      ]);
      setCategories(c);
      setAuthors(a);
      setBooks(b);

      if (!catId && c[0]) setCatId(String(c[0].id_cat));
      if (!authorId && a[0]) setAuthorId(String(a[0].id_auteur));
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function createCategory() {
    setError("");
    try {
      await post("/api/books/categories", { nom_cat: catName, champ: catChamp });
      setCatName("");
      setCatChamp("");
      await loadAll();
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  async function createAuthor() {
    setError("");
    try {
      await post("/api/books/authors", { nom_auteur: aNom, prenom_auteur: aPrenom });
      setANom("");
      setAPrenom("");
      await loadAll();
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  async function createBook() {
    setError("");
    try {
      await post("/api/books/books", {
        titre,
        isbn,
        quantite: Number(quantite),
        cat_id: Number(catId),
        auteur_ids: authorId ? [Number(authorId)] : [],
      });
      setTitre("");
      setIsbn("");
      setQuantite(1);
      await loadAll();
    } catch (e) {
      setError(e?.response?.data?.error || e.message);
    }
  }

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Books</h2>
        <Button variant="outline" onClick={loadAll}>Refresh</Button>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>Create category</CardTitle></CardHeader>
          <CardContent className="grid gap-3">
            <div className="grid gap-2">
              <Label>Nom</Label>
              <Input value={catName} onChange={(e) => setCatName(e.target.value)} placeholder="nom_cat" />
            </div>
            <div className="grid gap-2">
              <Label>Champ</Label>
              <Input value={catChamp} onChange={(e) => setCatChamp(e.target.value)} placeholder="champ" />
            </div>
            <Button onClick={createCategory}>Add</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Create author</CardTitle></CardHeader>
          <CardContent className="grid gap-3">
            <div className="grid gap-2">
              <Label>Nom</Label>
              <Input value={aNom} onChange={(e) => setANom(e.target.value)} placeholder="nom_auteur" />
            </div>
            <div className="grid gap-2">
              <Label>Prénom</Label>
              <Input value={aPrenom} onChange={(e) => setAPrenom(e.target.value)} placeholder="prenom_auteur" />
            </div>
            <Button onClick={createAuthor}>Add</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Create book</CardTitle></CardHeader>
          <CardContent className="grid gap-3">
            <div className="grid gap-2">
              <Label>Titre</Label>
              <Input value={titre} onChange={(e) => setTitre(e.target.value)} placeholder="titre" />
            </div>
            <div className="grid gap-2">
              <Label>ISBN</Label>
              <Input value={isbn} onChange={(e) => setIsbn(e.target.value)} placeholder="isbn" />
            </div>
            <div className="grid gap-2">
              <Label>Quantité</Label>
              <Input type="number" value={quantite} onChange={(e) => setQuantite(e.target.value)} />
            </div>

            <div className="grid gap-2">
              <Label>Category</Label>
              <Select value={catId} onValueChange={setCatId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((c) => (
                    <SelectItem key={c.id_cat} value={String(c.id_cat)}>
                      {c.nom_cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label>Author</Label>
              <Select value={authorId} onValueChange={setAuthorId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose author" />
                </SelectTrigger>
                <SelectContent>
                  {authors.map((a) => (
                    <SelectItem key={a.id_auteur} value={String(a.id_auteur)}>
                      {a.nom_auteur} {a.prenom_auteur}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button onClick={createBook}>Add</Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Catalog</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>ISBN</TableHead>
                  <TableHead>Qty</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Authors</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {books.map((b) => (
                  <TableRow key={b.id_livre}>
                    <TableCell className="font-medium">{b.id_livre}</TableCell>
                    <TableCell>{b.titre}</TableCell>
                    <TableCell>{b.isbn}</TableCell>
                    <TableCell>{b.quantite}</TableCell>
                    <TableCell>{b.categorie?.nom_cat || "-"}</TableCell>
                    <TableCell>
                      {(b.auteurs || []).map(a => `${a.nom_auteur} ${a.prenom_auteur}`).join(", ") || "-"}
                    </TableCell>
                  </TableRow>
                ))}
                {books.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      No books found.
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
