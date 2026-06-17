
import React, { useState } from 'react';
import { HashRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import {
  Home,
  Search,
  KeyRound,
  ShieldCheck,
  BookOpen,
  User,
  CheckCircle2,
} from 'lucide-react';
import Landing from './components/Landing';
import Browse from './components/Browse';
import Register from './components/Register';
import ActivateToken from './components/ActivateToken';
import AccountPage from './components/AccountPage';
import { Account } from './types';
import { getAccount } from './services/auth';

const App: React.FC = () => {
  const [account, setAccount] = useState<Account | null>(() => getAccount());
  const unlocked = !!account;

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 flex flex-col pb-20 md:pb-0 md:pl-64">
        {/* Mobile Header */}
        <header className="md:hidden bg-white border-b px-4 py-3 flex justify-between items-center sticky top-0 z-50">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <BookOpen className="text-white w-5 h-5" />
            </div>
            <span className="font-bold text-slate-800">ScholarHub</span>
          </Link>
          {unlocked ? (
            <span className="flex items-center gap-1 bg-green-50 text-green-700 px-2 py-1 rounded-full text-xs font-bold border border-green-200">
              <CheckCircle2 className="w-3 h-3" /> Unlocked
            </span>
          ) : (
            <Link to="/register" className="bg-slate-900 text-white px-3 py-1.5 rounded-full text-xs font-bold">
              Get Token
            </Link>
          )}
        </header>

        {/* Desktop Sidebar */}
        <aside className="hidden md:flex flex-col w-64 bg-white border-r fixed left-0 top-0 bottom-0 z-50">
          <div className="p-6">
            <Link to="/" className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 bg-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-200">
                <BookOpen className="text-white w-6 h-6" />
              </div>
              <span className="font-bold text-xl text-slate-800">ScholarHub</span>
            </Link>

            <nav className="space-y-1">
              <NavLink to="/" icon={<Home />} label="Home" />
              <NavLink to="/scholarships" icon={<Search />} label="Browse Scholarships" />
              {unlocked ? (
                <NavLink to="/account" icon={<User />} label="My Account" />
              ) : (
                <>
                  <NavLink to="/register" icon={<KeyRound />} label="Register" />
                  <NavLink to="/activate" icon={<ShieldCheck />} label="Activate Token" />
                </>
              )}
            </nav>
          </div>

          <div className="mt-auto p-4 border-t">
            <div className={`rounded-xl p-4 flex items-center gap-3 ${unlocked ? 'bg-green-50' : 'bg-slate-50'}`}>
              {unlocked ? (
                <>
                  <CheckCircle2 className="w-8 h-8 text-green-600 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-green-900 truncate">Full Access</p>
                    <p className="text-xs text-green-600 truncate">{account?.name}</p>
                  </div>
                </>
              ) : (
                <>
                  <KeyRound className="w-8 h-8 text-slate-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">Preview Mode</p>
                    <p className="text-xs text-slate-500 truncate">Register to unlock</p>
                  </div>
                </>
              )}
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-4 md:p-8 max-w-6xl mx-auto w-full">
          <Routes>
            <Route path="/" element={<Landing unlocked={unlocked} />} />
            <Route path="/scholarships" element={<Browse unlocked={unlocked} />} />
            <Route path="/register" element={<Register onRegister={setAccount} />} />
            <Route path="/activate" element={<ActivateToken onActivate={setAccount} />} />
            <Route
              path="/account"
              element={account ? <AccountPage account={account} onSignOut={() => setAccount(null)} /> : <Navigate to="/register" replace />}
            />
          </Routes>
        </main>

        {/* Mobile Navigation */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around items-center h-16 px-2 z-50">
          <MobileNavLink to="/" icon={<Home />} label="Home" />
          <MobileNavLink to="/scholarships" icon={<Search />} label="Browse" />
          {unlocked ? (
            <MobileNavLink to="/account" icon={<User />} label="Account" />
          ) : (
            <>
              <MobileNavLink to="/register" icon={<KeyRound />} label="Register" />
              <MobileNavLink to="/activate" icon={<ShieldCheck />} label="Activate" />
            </>
          )}
        </nav>
      </div>
    </Router>
  );
};

const NavLink: React.FC<{ to: string; icon: React.ReactNode; label: string }> = ({ to, icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
        isActive
          ? 'bg-green-50 text-green-700 font-semibold'
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'
      }`}
    >
      {React.cloneElement(icon as React.ReactElement, { className: `w-5 h-5 ${isActive ? 'text-green-600' : ''}` })}
      {label}
    </Link>
  );
};

const MobileNavLink: React.FC<{ to: string; icon: React.ReactNode; label: string }> = ({ to, icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link to={to} className="flex flex-col items-center gap-1">
      <div className={`p-1 rounded-lg transition-colors ${isActive ? 'text-green-600' : 'text-slate-400'}`}>
        {React.cloneElement(icon as React.ReactElement, { className: 'w-6 h-6' })}
      </div>
      <span className={`text-[10px] font-medium ${isActive ? 'text-green-600' : 'text-slate-400'}`}>{label}</span>
    </Link>
  );
};

export default App;
