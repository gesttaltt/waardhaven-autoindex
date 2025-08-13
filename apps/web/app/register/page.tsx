"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "../utils/api";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      const res = await api.post('/api/v1/auth/register', { 
        email, 
        password 
      });
      
      console.log('Registration successful:', res.data);
      localStorage.setItem("token", res.data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      console.error('Registration error:', err);
      console.error('Error details:', {
        message: err.message,
        code: err.code,
        response: err.response?.data,
        status: err.response?.status,
        headers: err.response?.headers,
        config: {
          url: err.config?.url,
          method: err.config?.method,
          baseURL: err.config?.baseURL
        }
      });
      
      // More detailed error handling
      if (err.response) {
        // Server responded with error
        const detail = err.response.data?.detail || err.response.data?.message || 'Unknown server error';
        setError(`Server error (${err.response.status}): ${detail}`);
      } else if (err.request) {
        // Request made but no response
        setError('Cannot connect to server. Please check if the API is running.');
      } else {
        // Request setup error
        setError('Error setting up request: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="card w-full max-w-md text-center">
        <h1 className="text-2xl font-semibold gradient-text mb-2">Create Account</h1>
        <p className="text-neutral-400 text-sm">Join the future of automated investing</p>
        <div className="mt-6 space-y-4">
          <input className="input" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <input className="input" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="btn-primary w-full" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
          <p className="text-xs text-neutral-500 mt-2">
            Platform in beta - Use at your own risk
          </p>
        </div>
      </form>
    </main>
  );
}
