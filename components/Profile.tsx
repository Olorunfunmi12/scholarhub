
import React from 'react';
import { UserProfile } from '../types';
import { Save, User as UserIcon, Mail, GraduationCap, BookOpen, Clock } from 'lucide-react';

interface ProfileProps {
  profile: UserProfile;
  setProfile: React.Dispatch<React.SetStateAction<UserProfile>>;
}

const Profile: React.FC<ProfileProps> = ({ profile, setProfile }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setProfile(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="relative">
          <div className="w-32 h-32 rounded-full border-4 border-white shadow-xl overflow-hidden bg-slate-100">
            <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${profile.name}`} alt="avatar" />
          </div>
          <div className="absolute bottom-1 right-1 w-8 h-8 bg-green-500 rounded-full border-4 border-white flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full animate-ping" />
          </div>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{profile.name}</h1>
          <p className="text-slate-500">Inventory ID: SCH-2024-{profile.points}</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-100 p-8 shadow-sm space-y-6">
        <h2 className="text-lg font-bold text-slate-800 border-b pb-4">Personal Information</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
              <UserIcon className="w-3 h-3" /> Full Name
            </label>
            <input 
              name="name"
              value={profile.name}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
              <Mail className="w-3 h-3" /> Email Address
            </label>
            <input 
              name="email"
              value={profile.email}
              onChange={handleChange}
              placeholder="email@example.com"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
              <BookOpen className="w-3 h-3" /> Undergraduate Major
            </label>
            <input 
              name="major"
              value={profile.major}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
              <GraduationCap className="w-3 h-3" /> Degree Target
            </label>
            <select 
              name="degreeTarget"
              value={profile.degreeTarget}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
            >
              <option value="Masters">Masters</option>
              <option value="PhD">PhD</option>
              <option value="PostDoc">PostDoc</option>
            </select>
          </div>
        </div>

        <button className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-slate-800 transition-all">
          <Save className="w-5 h-5" /> Save Inventory
        </button>
      </div>

      <div className="bg-slate-900 rounded-3xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-[-20px] right-[-20px] w-40 h-40 bg-green-500/20 rounded-full blur-3xl" />
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-6 text-center md:text-left">
          <div>
            <h3 className="text-xl font-bold mb-2">Annual Reward Program 🎁</h3>
            <p className="text-slate-400 text-sm max-w-xs">Accumulate points by searching and using tools. The most active Nigerian scholar wins ₦500,000 for flight tickets!</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md px-6 py-4 rounded-2xl border border-white/10">
            <span className="text-sm text-slate-400 font-medium block mb-1">Current Points</span>
            <span className="text-4xl font-bold text-green-400">{profile.points}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
