"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Debug environment
  console.log('Environment check:', {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    API_BEING_USED: API,
    NODE_ENV: process.env.NODE_ENV,
    allEnv: Object.keys(process.env).filter(k => k.startsWith('NEXT_PUBLIC'))
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    // Debug logging
    console.log('API URL:', API);
    console.log('Attempting registration to:', `${API}/api/v1/auth/register`);
    
    try {
      const res = await axios.post(`${API}/api/v1/auth/register`, { 
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
        setError(`Cannot connect to server at ${API}. Please check if the API is running.`);
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
      <form onSubmit={handleSubmit} className="card w-full max-w-md">
        <h1 className="text-2xl font-semibold">Create Account</h1>
        <div className="mt-6 space-y-4">
          <input className="input" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <input className="input" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="btn w-full" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
          <p className="text-xs text-gray-500 mt-2">
            This platform still in development phase, use at your own risk
          </p>
        </div>
      </form>
    </main>
  );
}
