
import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Search, 
  User, 
  Trophy, 
  Image as ImageIcon, 
  Bell, 
  ChevronRight,
  Plus,
  Zap,
  BookOpen,
  Send,
  Loader2,
  Settings
} from 'lucide-react';
import Dashboard from './components/Dashboard';
import SearchPortal from './components/SearchPortal';
import Profile from './components/Profile';
import Leaderboard from './components/Leaderboard';
import DocumentEditor from './components/DocumentEditor';
import { UserProfile } from './types';

const App: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile>(() => {
    const saved = localStorage.getItem('naija_scholar_profile');
    return saved ? JSON.parse(saved) : {
      name: 'Scholar Guest',
      email: '',
      major: 'Computer Science',
      degreeTarget: 'Masters',
      points: 10,
      activityHistory: [{ date: Date.now(), action: 'Joined ScholarHub' }]
    };
  });

  useEffect(() => {
    localStorage.setItem('naija_scholar_profile', JSON.stringify(profile));
  }, [profile]);

  const addPoints = (amount: number, action: string) => {
    setProfile(prev => ({
      ...prev,
      points: prev.points + amount,
      activityHistory: [{ date: Date.now(), action }, ...prev.activityHistory]
    }));
  };

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 flex flex-col pb-20 md:pb-0 md:pl-64">
        {/* Mobile Header */}
        <header className="md:hidden bg-white border-b px-4 py-3 flex justify-between items-center sticky top-0 z-50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <BookOpen className="text-white w-5 h-5" />
            </div>
            <span className="font-bold text-slate-800">ScholarHub</span>
          </div>
          <div className="flex items-center gap-3">
            <Bell className="w-5 h-5 text-slate-500" />
            <div className="flex items-center gap-1 bg-amber-50 text-amber-700 px-2 py-1 rounded-full text-xs font-bold border border-amber-200">
              <Zap className="w-3 h-3 fill-amber-500" />
              {profile.points}
            </div>
          </div>
        </header>

        {/* Desktop Sidebar */}
        <aside className="hidden md:flex flex-col w-64 bg-white border-r fixed left-0 top-0 bottom-0 z-50">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 bg-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-200">
                <BookOpen className="text-white w-6 h-6" />
              </div>
              <span className="font-bold text-xl text-slate-800">ScholarHub</span>
            </div>

            <nav className="space-y-1">
              <NavLink to="/" icon={<Home />} label="Dashboard" />
              <NavLink to="/search" icon={<Search />} label="Find Scholarships" />
              <NavLink to="/editor" icon={<ImageIcon />} label="Doc Editor" />
              <NavLink to="/leaderboard" icon={<Trophy />} label="Leaderboard" />
              <NavLink to="/profile" icon={<User />} label="My Inventory" />
            </nav>
          </div>

          <div className="mt-auto p-4 border-t">
            <div className="bg-slate-50 rounded-xl p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 overflow-hidden border-2 border-white">
                <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${profile.name}`} alt="avatar" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900 truncate">{profile.name}</p>
                <p className="text-xs text-slate-500 truncate">{profile.degreeTarget} aspirant</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-4 md:p-8 max-w-6xl mx-auto w-full">
          <Routes>
            <Route path="/" element={<Dashboard profile={profile} />} />
            <Route path="/search" element={<SearchPortal addPoints={addPoints} />} />
            <Route path="/editor" element={<DocumentEditor addPoints={addPoints} />} />
            <Route path="/leaderboard" element={<Leaderboard currentPoints={profile.points} />} />
            <Route path="/profile" element={<Profile profile={profile} setProfile={setProfile} />} />
          </Routes>
        </main>

        {/* Mobile Navigation */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around items-center h-16 px-2 z-50">
          <MobileNavLink to="/" icon={<Home />} label="Home" />
          <MobileNavLink to="/search" icon={<Search />} label="Search" />
          <MobileNavLink to="/editor" icon={<ImageIcon />} label="Edit" />
          <MobileNavLink to="/leaderboard" icon={<Trophy />} label="Winners" />
          <MobileNavLink to="/profile" icon={<User />} label="Me" />
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
