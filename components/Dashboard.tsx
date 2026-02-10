
import React from 'react';
import { UserProfile, Scholarship } from '../types';
import { 
  Zap, 
  TrendingUp, 
  Globe, 
  Award, 
  Clock,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

const Dashboard: React.FC<{ profile: UserProfile }> = ({ profile }) => {
  const featuredScholarships: Scholarship[] = [
    {
      id: '1',
      title: 'Chevening Scholarship 2025',
      country: 'UK',
      deadline: 'Nov 2024',
      funding: 'Full',
      degree: 'Masters',
      description: 'Fully funded UK government scholarship for outstanding leaders from Nigeria.',
      link: 'https://www.chevening.org/apply/',
      addedAt: Date.now()
    },
    {
      id: '2',
      title: 'DAAD EPOS Scholarship',
      country: 'Germany',
      deadline: 'Aug-Oct 2024',
      funding: 'Full',
      degree: 'Masters',
      description: 'Development-Related Postgraduate Courses in Germany with full monthly stipend.',
      link: 'https://www.daad.de/en/',
      addedAt: Date.now()
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <section className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {profile.name.split(' ')[0]}! 🇳🇬</h1>
        <p className="text-slate-500">You're in the top 15% of active scholars this month. Keep it up!</p>
      </section>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard 
          icon={<Zap className="text-amber-500" />} 
          label="Activity Points" 
          value={profile.points.toString()} 
          sub="Rank #42" 
          color="bg-amber-50" 
        />
        <StatCard 
          icon={<Award className="text-blue-500" />} 
          label="Scholarships Found" 
          value="124" 
          sub="+12 this week" 
          color="bg-blue-50" 
        />
        <StatCard 
          icon={<TrendingUp className="text-green-500" />} 
          label="Application Rate" 
          value="85%" 
          sub="Global average: 40%" 
          color="bg-green-50" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Featured Section */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-slate-800">Hot Opportunities</h2>
            <button className="text-sm font-medium text-green-600 hover:underline flex items-center gap-1">
              View all <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-4">
            {featuredScholarships.map(s => (
              <div key={s.id} className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all group">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded uppercase tracking-wider">{s.funding}</span>
                    <span className="px-2 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded uppercase tracking-wider">{s.country}</span>
                  </div>
                  <span className="text-xs text-red-500 font-medium flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Ends {s.deadline}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 mb-2 group-hover:text-green-600 transition-colors">{s.title}</h3>
                <p className="text-sm text-slate-600 mb-4 line-clamp-2">{s.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-medium">Added 2 days ago</span>
                  <a href={s.link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-sm font-semibold text-green-600 hover:bg-green-50 px-3 py-1 rounded-lg transition-colors">
                    Apply <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-slate-800">Inventory Feed</h2>
          <div className="bg-white rounded-2xl border border-slate-100 p-6 space-y-6">
            {profile.activityHistory.slice(0, 5).map((act, i) => (
              <div key={i} className="flex gap-4 relative">
                {i !== 4 && <div className="absolute left-2 top-6 bottom-[-1.5rem] w-0.5 bg-slate-100" />}
                <div className="w-4 h-4 rounded-full bg-green-500 border-2 border-white shadow-sm z-10 mt-1 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-800">{act.action}</p>
                  <p className="text-xs text-slate-400">{new Date(act.date).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
            <button className="w-full py-3 bg-slate-50 text-slate-500 text-sm font-medium rounded-xl hover:bg-slate-100 transition-colors">
              Show Full Log
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard: React.FC<{ icon: React.ReactNode; label: string; value: string; sub: string; color: string }> = ({ icon, label, value, sub, color }) => (
  <div className={`p-6 rounded-2xl border border-slate-100 bg-white shadow-sm`}>
    <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center mb-4`}>
      {icon}
    </div>
    <p className="text-sm text-slate-500 font-medium mb-1">{label}</p>
    <div className="flex items-baseline gap-2">
      <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
      <span className="text-xs text-slate-400">{sub}</span>
    </div>
  </div>
);

export default Dashboard;
