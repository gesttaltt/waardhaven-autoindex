"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  // Temporary hardcode while debugging env var issue
  const API = 'https://waardhaven-api.onrender.com';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await axios.post(`${API}/api/v1/auth/login`, { email, password });
      localStorage.setItem("token", res.data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="card w-full max-w-md">
        <h1 className="text-2xl font-semibold">Log In</h1>
        <div className="mt-6 space-y-4">
          <input className="input" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <input className="input" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="btn w-full" type="submit">Log In</button>
        </div>
      </form>
    </main>
  );
}
