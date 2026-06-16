
import React from 'react';
import { Link } from 'react-router-dom';
import { Globe2, ShieldCheck, Search, KeyRound, ArrowRight, GraduationCap } from 'lucide-react';
import { scholarships } from '../data/scholarships';
import ScholarshipCard from './ScholarshipCard';

const Landing: React.FC<{ unlocked: boolean }> = ({ unlocked }) => {
  const featured = scholarships.slice(0, 3);
  const countries = new Set(scholarships.map(s => s.country)).size;

  return (
    <div className="space-y-20 pb-10">
      {/* Hero */}
      <section className="text-center max-w-3xl mx-auto pt-8 space-y-6 animate-in fade-in duration-500">
        <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-50 text-green-700 rounded-full text-xs font-bold uppercase tracking-wider">
          <GraduationCap className="w-3.5 h-3.5" /> 2026 & Beyond Scholarship Cycle
        </span>
        <h1 className="text-4xl md:text-5xl font-bold text-slate-900 leading-tight">
          Find Your Fully-Funded <span className="text-green-600">Graduate Scholarship</span>, Anywhere in the World
        </h1>
        <p className="text-slate-500 text-lg">
          ScholarHub curates verified Masters, PhD, and PostDoc funding opportunities from {countries}+ countries.
          Browse for free, register for an access token, and unlock full details, deadlines, and direct apply links.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
          <Link to="/scholarships" className="px-6 py-3 bg-green-600 text-white rounded-xl font-bold hover:bg-green-700 transition-colors flex items-center justify-center gap-2">
            <Search className="w-5 h-5" /> Browse Scholarships
          </Link>
          {!unlocked && (
            <Link to="/register" className="px-6 py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-colors flex items-center justify-center gap-2">
              <KeyRound className="w-5 h-5" /> Get Full Access
            </Link>
          )}
        </div>
      </section>

      {/* Stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
        {[
          { label: 'Scholarships Listed', value: `${scholarships.length}+` },
          { label: 'Countries Covered', value: `${countries}` },
          { label: 'Fully Funded', value: `${scholarships.filter(s => s.funding === 'Full').length}` },
          { label: 'Open for 2026+', value: '100%' },
        ].map((stat, i) => (
          <div key={i} className="bg-white rounded-2xl border border-slate-100 p-5 text-center shadow-sm">
            <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
            <p className="text-xs text-slate-500 font-medium">{stat.label}</p>
          </div>
        ))}
      </section>

      {/* Featured */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-slate-900">Featured Opportunities</h2>
          <p className="text-slate-500">A preview of what's waiting inside ScholarHub.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {featured.map(s => <ScholarshipCard key={s.id} scholarship={s} unlocked={unlocked} />)}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-white rounded-3xl border border-slate-100 p-8 md:p-12 space-y-8">
        <h2 className="text-2xl font-bold text-slate-900 text-center">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Step icon={<Search />} title="1. Browse" text="Search and filter graduate scholarships by country, degree, and funding type — no signup required." />
          <Step icon={<KeyRound />} title="2. Register" text="Create your free client profile in seconds. We instantly generate your personal access token." />
          <Step icon={<ShieldCheck />} title="3. Unlock" text="Activate your token to see full descriptions, deadlines, and apply directly on the official site." />
        </div>
      </section>

      <section className="bg-slate-900 rounded-3xl p-8 md:p-12 text-white text-center space-y-4 relative overflow-hidden">
        <div className="absolute top-[-40px] right-[-40px] w-64 h-64 bg-green-500/20 rounded-full blur-3xl" />
        <Globe2 className="w-10 h-10 text-green-400 mx-auto" />
        <h2 className="text-2xl font-bold">Your global scholarship search starts here.</h2>
        <p className="text-slate-400 max-w-xl mx-auto">Join now and get a personal access token — free, instant, and yours to activate on any device.</p>
        <Link to="/register" className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 rounded-xl font-bold hover:bg-green-700 transition-colors">
          Register for Your Token <ArrowRight className="w-4 h-4" />
        </Link>
      </section>
    </div>
  );
};

const Step: React.FC<{ icon: React.ReactNode; title: string; text: string }> = ({ icon, title, text }) => (
  <div className="text-center space-y-3">
    <div className="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center mx-auto">
      {React.cloneElement(icon as React.ReactElement, { className: 'w-6 h-6' })}
    </div>
    <h3 className="font-bold text-slate-900">{title}</h3>
    <p className="text-sm text-slate-500">{text}</p>
  </div>
);

export default Landing;
