
import React, { useMemo, useState } from 'react';
import { Search, Loader2, Globe, Info, Lock, Sparkles } from 'lucide-react';
import { scholarships as allScholarships, COUNTRIES, DEGREES, FUNDING_TYPES } from '../data/scholarships';
import { searchScholarships } from '../services/geminiService';
import { Scholarship } from '../types';
import ScholarshipCard from './ScholarshipCard';
import { Link } from 'react-router-dom';

const Browse: React.FC<{ unlocked: boolean }> = ({ unlocked }) => {
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('');
  const [degree, setDegree] = useState('');
  const [funding, setFunding] = useState('');

  const [aiQuery, setAiQuery] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResults, setAiResults] = useState<Scholarship[]>([]);
  const [aiSources, setAiSources] = useState<any[]>([]);

  const filtered = useMemo(() => {
    return allScholarships.filter(s => {
      if (country && s.country !== country) return false;
      if (degree && s.degree !== degree) return false;
      if (funding && s.funding !== funding) return false;
      if (keyword) {
        const k = keyword.toLowerCase();
        return s.title.toLowerCase().includes(k) || s.field.toLowerCase().includes(k) || s.country.toLowerCase().includes(k);
      }
      return true;
    });
  }, [keyword, country, degree, funding]);

  const handleAiSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuery.trim() || !unlocked) return;
    setAiLoading(true);
    try {
      const data = await searchScholarships(aiQuery);
      setAiResults(data.scholarships);
      setAiSources(data.sources);
    } catch (error) {
      console.error(error);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">Browse Graduate Scholarships</h1>
        <p className="text-slate-500">{allScholarships.length} curated opportunities open for 2026 and beyond.</p>
      </div>

      {!unlocked && (
        <div className="flex items-center gap-3 text-sm bg-amber-50 border border-amber-100 text-amber-800 p-4 rounded-xl">
          <Lock className="w-5 h-5 shrink-0" />
          <p>
            You're browsing in preview mode. <Link to="/register" className="font-bold underline">Register for a free access token</Link> to unlock full descriptions and direct apply links.
          </p>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white border border-slate-100 rounded-2xl p-5 grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="relative md:col-span-2">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            placeholder="Search by title, field, or country"
            className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500 text-sm"
          />
        </div>
        <select value={country} onChange={e => setCountry(e.target.value)} className="px-3 py-2.5 bg-slate-50 border border-slate-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-green-500">
          <option value="">All Countries</option>
          {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={degree} onChange={e => setDegree(e.target.value)} className="px-3 py-2.5 bg-slate-50 border border-slate-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-green-500">
          <option value="">All Degrees</option>
          {DEGREES.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
        <select value={funding} onChange={e => setFunding(e.target.value)} className="px-3 py-2.5 bg-slate-50 border border-slate-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-green-500 md:col-start-4">
          <option value="">All Funding Types</option>
          {FUNDING_TYPES.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(s => <ScholarshipCard key={s.id} scholarship={s} unlocked={unlocked} />)}
      </div>
      {filtered.length === 0 && (
        <p className="text-center text-slate-400 py-10">No scholarships match those filters.</p>
      )}

      {/* AI Live Search - premium feature */}
      <div className="bg-white border border-slate-100 rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-green-600" />
          <h2 className="text-lg font-bold text-slate-900">Live AI Search</h2>
          <span className="text-[10px] font-bold bg-green-50 text-green-700 px-2 py-0.5 rounded uppercase">Token Members Only</span>
        </div>
        <p className="text-sm text-slate-500">Ask in plain language and we'll search the live web for fresh matches, e.g. "fully funded PhD in robotics in Europe".</p>

        {unlocked ? (
          <>
            <form onSubmit={handleAiSearch} className="relative">
              <input
                value={aiQuery}
                onChange={e => setAiQuery(e.target.value)}
                placeholder="e.g. Master's in Artificial Intelligence fully funded in Europe"
                className="w-full pl-4 pr-28 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-2 focus:ring-green-500 text-sm"
              />
              <button
                type="submit"
                disabled={aiLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-green-600 text-white px-5 py-1.5 rounded-lg font-semibold hover:bg-green-700 disabled:bg-slate-300 transition-colors text-sm"
              >
                {aiLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
              </button>
            </form>

            {aiResults.length > 0 && (
              <div className="space-y-4 pt-2">
                <div className="flex items-center gap-2 text-sm text-slate-500 bg-blue-50 p-3 rounded-xl border border-blue-100">
                  <Info className="w-4 h-4 text-blue-500 shrink-0" />
                  <p>Found <strong>{aiResults.length}</strong> live matches.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {aiResults.map((s, i) => <ScholarshipCard key={i} scholarship={s} unlocked={unlocked} />)}
                </div>
                {aiSources.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {aiSources.map((source: any, i: number) => (
                      <a key={i} href={source.web?.uri} target="_blank" rel="noopener noreferrer" className="text-xs px-3 py-1 bg-slate-50 text-slate-600 border border-slate-200 rounded-full hover:bg-slate-100 flex items-center gap-1">
                        <Globe className="w-3 h-3" /> {source.web?.title || `Source ${i + 1}`}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <Link to="/register" className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl font-semibold hover:bg-slate-800 transition-colors">
            <Lock className="w-4 h-4" /> Unlock Live AI Search
          </Link>
        )}
      </div>
    </div>
  );
};

export default Browse;
