
import React from 'react';
import { Trophy, Medal, Award, Flame, Star, ChevronUp } from 'lucide-react';

const Leaderboard: React.FC<{ currentPoints: number }> = ({ currentPoints }) => {
  const users = [
    { name: "Olawale Johnson", points: 2450, rank: 1, trend: 'up' },
    { name: "Chinelo Okeke", points: 2310, rank: 2, trend: 'stable' },
    { name: "Aminu Ibrahim", points: 2100, rank: 3, trend: 'up' },
    { name: "Blessing Adeyemi", points: 1950, rank: 4, trend: 'down' },
    { name: "Tunde Ednut", points: 1800, rank: 5, trend: 'up' },
    { name: "You", points: currentPoints, rank: 42, trend: 'up' },
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-10">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">Scholar Leaderboard 🏆</h1>
        <p className="text-slate-500">The most active scholars for the 2024/2025 cycle.</p>
      </div>

      {/* Podium */}
      <div className="flex justify-center items-end gap-2 md:gap-8 pt-10">
        {/* 2nd */}
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 md:w-24 md:h-24 rounded-full border-4 border-slate-200 overflow-hidden bg-white shadow-lg">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Chinelo" alt="avatar" />
            </div>
            <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center border-2 border-white">
              <Medal className="w-4 h-4 text-slate-600" />
            </div>
          </div>
          <div className="w-24 md:w-32 h-24 bg-slate-200 rounded-t-2xl flex flex-col items-center justify-center p-2 shadow-sm">
            <span className="font-bold text-slate-700 truncate w-full text-center">{users[1].name.split(' ')[0]}</span>
            <span className="text-xs font-bold text-slate-500">{users[1].points} pts</span>
          </div>
        </div>

        {/* 1st */}
        <div className="flex flex-col items-center gap-4 scale-110">
          <div className="relative">
            <div className="w-20 h-20 md:w-28 md:h-28 rounded-full border-4 border-amber-400 overflow-hidden bg-white shadow-xl">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Olawale" alt="avatar" />
            </div>
            <div className="absolute -top-6 left-1/2 -translate-x-1/2">
              <Trophy className="w-8 h-8 text-amber-400 drop-shadow" />
            </div>
            <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-amber-400 rounded-full flex items-center justify-center border-4 border-white">
              <Medal className="w-5 h-5 text-white" />
            </div>
          </div>
          <div className="w-28 md:w-36 h-36 bg-amber-50 border-x border-t border-amber-200 rounded-t-3xl flex flex-col items-center justify-center p-2 shadow-lg">
            <span className="font-bold text-amber-900 truncate w-full text-center">{users[0].name.split(' ')[0]}</span>
            <span className="text-sm font-bold text-amber-600">{users[0].points} pts</span>
          </div>
        </div>

        {/* 3rd */}
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 md:w-24 md:h-24 rounded-full border-4 border-orange-200 overflow-hidden bg-white shadow-lg">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Aminu" alt="avatar" />
            </div>
            <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-orange-200 rounded-full flex items-center justify-center border-2 border-white">
              <Medal className="w-4 h-4 text-orange-600" />
            </div>
          </div>
          <div className="w-24 md:w-32 h-20 bg-orange-100 rounded-t-2xl flex flex-col items-center justify-center p-2 shadow-sm">
            <span className="font-bold text-orange-900 truncate w-full text-center">{users[2].name.split(' ')[0]}</span>
            <span className="text-xs font-bold text-orange-600">{users[2].points} pts</span>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="p-6 border-b bg-slate-50 flex justify-between items-center">
          <h3 className="font-bold text-slate-800">Top Inventory Holders</h3>
          <div className="flex items-center gap-1 text-xs text-slate-400">
            <Clock className="w-3 h-3" /> Resets in 12 days
          </div>
        </div>
        <div className="divide-y">
          {users.map((user, i) => (
            <div 
              key={i} 
              className={`flex items-center gap-4 p-5 transition-colors ${user.rank === 42 ? 'bg-green-50' : 'hover:bg-slate-50'}`}
            >
              <div className="w-8 text-center font-bold text-slate-400">
                {user.rank}
              </div>
              <div className="w-10 h-10 rounded-full bg-slate-100 overflow-hidden border">
                <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`} alt="avatar" />
              </div>
              <div className="flex-1">
                <p className="font-bold text-slate-800 flex items-center gap-2">
                  {user.name}
                  {user.rank <= 3 && <Star className="w-3 h-3 text-amber-400 fill-amber-400" />}
                </p>
                <p className="text-xs text-slate-400">Nigeria Scholar</p>
              </div>
              <div className="text-right">
                <p className="font-bold text-slate-900">{user.points} pts</p>
                <div className={`text-[10px] flex items-center justify-end gap-0.5 ${user.trend === 'up' ? 'text-green-500' : user.trend === 'down' ? 'text-red-500' : 'text-slate-400'}`}>
                  {user.trend === 'up' ? <ChevronUp className="w-3 h-3" /> : null}
                  {user.trend}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="p-6 bg-gradient-to-r from-green-600 to-emerald-600 rounded-3xl text-white flex flex-col md:flex-row items-center gap-6 shadow-xl shadow-green-100">
        <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center shrink-0">
          <Flame className="w-8 h-8 text-white animate-bounce" />
        </div>
        <div>
          <h4 className="text-lg font-bold mb-1">Scholarship Grant Challenge!</h4>
          <p className="text-white/80 text-sm">Every month, the top 3 users get a data stipend of 20GB and a certificate of excellence from the WhatsApp Group admin.</p>
        </div>
        <button className="md:ml-auto whitespace-nowrap bg-white text-green-700 px-6 py-2 rounded-xl font-bold hover:bg-slate-50 transition-colors">
          Join Challenge
        </button>
      </div>
    </div>
  );
};

const Clock = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
);

export default Leaderboard;
