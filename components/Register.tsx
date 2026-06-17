
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { KeyRound, Copy, Check, ArrowRight } from 'lucide-react';
import { registerAccount } from '../services/auth';
import { Account } from '../types';

const Register: React.FC<{ onRegister: (account: Account) => void }> = ({ onRegister }) => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', country: '', degreeTarget: 'Masters' });
  const [account, setAccount] = useState<Account | null>(null);
  const [copied, setCopied] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim()) return;
    const created = registerAccount(form);
    setAccount(created);
    onRegister(created);
  };

  const copyToken = () => {
    if (!account) return;
    navigator.clipboard.writeText(account.token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (account) {
    return (
      <div className="max-w-md mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="text-center space-y-2">
          <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto">
            <Check className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">You're registered, {account.name.split(' ')[0]}!</h1>
          <p className="text-slate-500">Here's your personal access token. Save it — you'll need it to unlock ScholarHub on any device.</p>
        </div>
        <div className="bg-slate-900 text-white rounded-2xl p-6 flex items-center justify-between gap-4">
          <span className="font-mono text-xl font-bold tracking-wider">{account.token}</span>
          <button onClick={copyToken} className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
            {copied ? <Check className="w-5 h-5 text-green-400" /> : <Copy className="w-5 h-5" />}
          </button>
        </div>
        <button
          onClick={() => navigate('/scholarships')}
          className="w-full py-3 bg-green-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-green-700 transition-colors"
        >
          Go to Full Scholarship Access <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center mx-auto">
          <KeyRound className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900">Register for Full Access</h1>
        <p className="text-slate-500">Create your free client profile and get an instant access token.</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-100 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase">Full Name</label>
          <input name="name" value={form.name} onChange={handleChange} required className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase">Email Address</label>
          <input type="email" name="email" value={form.email} onChange={handleChange} required className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase">Country of Residence</label>
          <input name="country" value={form.country} onChange={handleChange} className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase">Degree Target</label>
          <select name="degreeTarget" value={form.degreeTarget} onChange={handleChange} className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500">
            <option value="Masters">Masters</option>
            <option value="PhD">PhD</option>
            <option value="PostDoc">PostDoc</option>
          </select>
        </div>
        <button type="submit" className="w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-colors">
          Create My Access Token
        </button>
      </form>

      <p className="text-center text-sm text-slate-500">
        Already registered? <Link to="/activate" className="font-bold text-green-600 hover:underline">Activate your token</Link>
      </p>
    </div>
  );
};

export default Register;
