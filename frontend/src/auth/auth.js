const KEY = "lm_user";

export function saveUser(user) {
  localStorage.setItem(KEY, JSON.stringify(user));
}
export function loadUser() {
  const raw = localStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : null;
}
export function clearUser() {
  localStorage.removeItem(KEY);
}
export function isAdmin(user) {
  return user?.profil?.nom_p === "ADMIN";
}
