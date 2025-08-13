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
      
      // More detailed error handling
      if (err.response) {
        // Server responded with error
        console.error('Error response:', err.response.data);
        setError(err.response.data?.detail || `Server error: ${err.response.status}`);
      } else if (err.request) {
        // Request made but no response
        console.error('No response from server');
        setError('Cannot connect to server. Check if API URL is correct and server is running.');
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
          {/* Debug info - remove in production */}
          <p className="text-xs text-gray-500 mt-2">
            API: {API || 'Not set'}
          </p>
        </div>
      </form>
    </main>
  );
}
