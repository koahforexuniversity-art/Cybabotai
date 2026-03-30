const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";

export interface AuthUser {
  id: string;
  email: string;
  name: string | null;
  credits_balance: number;
  role: string;
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw) as AuthUser; } catch { return null; }
}

export function saveAuth(token: string, user: AuthUser) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function apiRegister(email: string, password: string, name: string) {
  const res = await fetch(`${BACKEND}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Registration failed");
  saveAuth(data.access_token, data.user);
  return data;
}

export async function apiLogin(email: string, password: string) {
  const res = await fetch(`${BACKEND}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  saveAuth(data.access_token, data.user);
  return data;
}
