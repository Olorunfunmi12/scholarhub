
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, AlertCircle, ArrowRight } from 'lucide-react';
import { activateAccount } from '../services/auth';
import { Account } from '../types';

const ActivateToken: React.FC<{ onActivate: (account: Account) => void }> = ({ onActivate }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const account = activateAccount(email, token, name || 'Scholar');
    if (!account) {
      setError('That token does not match this email. Double-check both fields or register for a new one.');
      return;
    }
    onActivate(account);
    navigate('/scholarships');
  };

  return (
    <div className="max-w-md mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center mx-auto">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900">Activate Your Token</h1>
        <p className="text-slate-500">Already registered on another device? Unlock full access here.</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-100 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase">Your Name</label>
          <input value={name} onChange={e => setName(e.target.value)} className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase">Email Used to Register</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase">Access Token</label>
          <input value={token} onChange={e => setToken(e.target.value)} required placeholder="SH-XXXX-XXXX" className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500 font-mono" />
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-100 p-3 rounded-xl">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        <button type="submit" className="w-full py-3 bg-green-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-green-700 transition-colors">
          Unlock Full Access <ArrowRight className="w-4 h-4" />
        </button>
      </form>

      <p className="text-center text-sm text-slate-500">
        Don't have a token yet? <Link to="/register" className="font-bold text-green-600 hover:underline">Register for free</Link>
      </p>
    </div>
  );
};

export default ActivateToken;
