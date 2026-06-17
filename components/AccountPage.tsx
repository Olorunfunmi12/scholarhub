
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Copy, Check, LogOut, Mail, Globe, GraduationCap, KeyRound } from 'lucide-react';
import { Account } from '../types';
import { signOut } from '../services/auth';

const AccountPage: React.FC<{ account: Account; onSignOut: () => void }> = ({ account, onSignOut }) => {
  const navigate = useNavigate();
  const [copied, setCopied] = React.useState(false);

  const copyToken = () => {
    navigator.clipboard.writeText(account.token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSignOut = () => {
    signOut();
    onSignOut();
    navigate('/');
  };

  return (
    <div className="max-w-xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col items-center gap-3 text-center">
        <div className="w-24 h-24 rounded-full border-4 border-white shadow-xl overflow-hidden bg-slate-100">
          <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${account.name}`} alt="avatar" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{account.name}</h1>
          <p className="text-slate-500 text-sm">Full Access Member</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-100 p-6 space-y-4 shadow-sm">
        <Row icon={<Mail className="w-4 h-4" />} label="Email" value={account.email} />
        {account.country && <Row icon={<Globe className="w-4 h-4" />} label="Country" value={account.country} />}
        {account.degreeTarget && <Row icon={<GraduationCap className="w-4 h-4" />} label="Degree Target" value={account.degreeTarget} />}
      </div>

      <div className="bg-slate-900 rounded-3xl p-6 text-white space-y-3">
        <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-slate-400">
          <KeyRound className="w-4 h-4" /> Your Access Token
        </div>
        <div className="flex items-center justify-between gap-4">
          <span className="font-mono text-xl font-bold tracking-wider">{account.token}</span>
          <button onClick={copyToken} className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
            {copied ? <Check className="w-5 h-5 text-green-400" /> : <Copy className="w-5 h-5" />}
          </button>
        </div>
        <p className="text-xs text-slate-400">Use this token with your email on any device to unlock full access.</p>
      </div>

      <button onClick={handleSignOut} className="w-full py-3 bg-white border border-slate-200 text-slate-600 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-slate-50 transition-colors">
        <LogOut className="w-4 h-4" /> Sign Out of This Device
      </button>
    </div>
  );
};

const Row: React.FC<{ icon: React.ReactNode; label: string; value: string }> = ({ icon, label, value }) => (
  <div className="flex items-center justify-between border-b border-slate-50 pb-3 last:border-0 last:pb-0">
    <span className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase">{icon} {label}</span>
    <span className="text-slate-900 font-medium">{value}</span>
  </div>
);

export default AccountPage;
