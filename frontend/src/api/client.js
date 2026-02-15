import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export async function get(url, config) {
  const res = await api.get(url, config);
  return res.data;
}
export async function post(url, body, config) {
  const res = await api.post(url, body, config);
  return res.data;
}
export async function put(url, body, config) {
  const res = await api.put(url, body, config);
  return res.data;
}
export async function del(url, config) {
  const res = await api.delete(url, config);
  return res.data;
}
