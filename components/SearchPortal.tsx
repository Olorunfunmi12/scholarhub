
import React, { useState } from 'react';
import { Search, Loader2, ExternalLink, Globe, Info, Filter } from 'lucide-react';
import { searchScholarships } from '../services/geminiService';
import { Scholarship, GroundingChunk } from '../types';

interface SearchPortalProps {
  addPoints: (points: number, action: string) => void;
}

const SearchPortal: React.FC<SearchPortalProps> = ({ addPoints }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Scholarship[]>([]);
  const [sources, setSources] = useState<any[]>([]);

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchScholarships(query);
      setResults(data.scholarships);
      setSources(data.sources);
      addPoints(5, `Searched for: ${query}`);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">Live Global Search 🌍</h1>
        <p className="text-slate-500">Connected to Google Search. Get the latest verified scholarship data for Nigerians.</p>
      </div>

      <form onSubmit={handleSearch} className="relative group">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Master's in Artificial Intelligence fully funded in Europe"
          className="w-full pl-12 pr-28 py-4 bg-white border border-slate-200 rounded-2xl shadow-sm focus:ring-2 focus:ring-green-500 outline-none transition-all group-hover:border-green-300"
        />
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-green-500 transition-colors w-5 h-5" />
        <button 
          type="submit"
          disabled={loading}
          className="absolute right-2 top-1/2 -translate-y-1/2 bg-green-600 text-white px-6 py-2 rounded-xl font-semibold hover:bg-green-700 disabled:bg-slate-300 transition-colors"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
        </button>
      </form>

      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-400 space-y-4">
          <div className="relative">
            <Loader2 className="w-12 h-12 animate-spin text-green-500" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Globe className="w-5 h-5 text-green-300" />
            </div>
          </div>
          <p className="animate-pulse">Scouring the web for the best opportunities...</p>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-8 pb-10">
          <div className="flex items-center gap-2 text-sm text-slate-500 bg-blue-50 p-4 rounded-xl border border-blue-100">
            <Info className="w-4 h-4 text-blue-500 shrink-0" />
            <p>Found <strong>{results.length}</strong> verified opportunities. We've sourced data from top platforms like Chevening, DAAD, and more.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {results.map((s, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-2xl p-5 hover:shadow-lg transition-all border-l-4 border-l-green-500">
                <div className="flex justify-between items-start mb-4">
                  <span className="px-2 py-0.5 bg-green-50 text-green-700 text-[10px] font-bold rounded uppercase tracking-wider">{s.funding}</span>
                  <span className="text-[10px] font-bold text-slate-400 bg-slate-50 px-2 py-0.5 rounded">{s.degree}</span>
                </div>
                <h3 className="font-bold text-slate-900 mb-2 leading-tight">{s.title}</h3>
                <div className="flex items-center gap-2 text-xs text-slate-500 mb-4">
                  <Globe className="w-3 h-3" /> <span>{s.country}</span>
                  <span className="w-1 h-1 bg-slate-300 rounded-full" />
                  <span className="text-red-500 font-medium">Deadline: {s.deadline}</span>
                </div>
                <p className="text-sm text-slate-600 mb-6 line-clamp-3">{s.description}</p>
                <a 
                  href={s.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-full py-2 bg-slate-50 border border-slate-100 text-slate-700 font-semibold rounded-xl text-center hover:bg-green-600 hover:text-white hover:border-green-600 transition-all flex items-center justify-center gap-2"
                >
                  Apply Now <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            ))}
          </div>

          {sources.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-slate-100">
              <h4 className="text-sm font-bold text-slate-900 mb-4">Verification Sources:</h4>
              <div className="flex flex-wrap gap-2">
                {sources.map((source: any, i: number) => (
                  <a 
                    key={i} 
                    href={source.web?.uri} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs px-3 py-1 bg-slate-50 text-slate-600 border border-slate-200 rounded-full hover:bg-slate-100"
                  >
                    {source.web?.title || 'Source ' + (i+1)}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="py-20 text-center space-y-4">
          <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto text-slate-300">
            <Search className="w-10 h-10" />
          </div>
          <div className="space-y-1">
            <p className="text-slate-900 font-semibold">Ready to find your path?</p>
            <p className="text-slate-400 text-sm">Enter a major or country to start searching.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPortal;
