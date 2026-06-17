
import React from 'react';
import { Globe, Clock, ExternalLink, Lock, GraduationCap } from 'lucide-react';
import { Scholarship } from '../types';
import { Link } from 'react-router-dom';

const fundingColor: Record<string, string> = {
  Full: 'bg-green-100 text-green-700',
  Partial: 'bg-amber-100 text-amber-700',
  'Tuition Only': 'bg-blue-100 text-blue-700',
};

const ScholarshipCard: React.FC<{ scholarship: Scholarship; unlocked: boolean }> = ({ scholarship: s, unlocked }) => {
  return (
    <div className="bg-white border border-slate-100 rounded-2xl p-5 hover:shadow-lg transition-all border-l-4 border-l-green-500 flex flex-col">
      <div className="flex justify-between items-start mb-3">
        <span className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase tracking-wider ${fundingColor[s.funding]}`}>{s.funding}</span>
        <span className="text-[10px] font-bold text-slate-400 bg-slate-50 px-2 py-0.5 rounded flex items-center gap-1">
          <GraduationCap className="w-3 h-3" /> {s.degree}
        </span>
      </div>
      <h3 className="font-bold text-slate-900 mb-2 leading-tight">{s.title}</h3>
      <div className="flex items-center gap-2 text-xs text-slate-500 mb-3 flex-wrap">
        <Globe className="w-3 h-3" /> <span>{s.country}</span>
        <span className="w-1 h-1 bg-slate-300 rounded-full" />
        <span className="text-red-500 font-medium flex items-center gap-1"><Clock className="w-3 h-3" /> {s.deadline}</span>
      </div>

      {unlocked ? (
        <>
          <p className="text-sm text-slate-600 mb-6 flex-1">{s.description}</p>
          <a
            href={s.link}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-2 bg-slate-50 border border-slate-100 text-slate-700 font-semibold rounded-xl text-center hover:bg-green-600 hover:text-white hover:border-green-600 transition-all flex items-center justify-center gap-2"
          >
            Apply Now <ExternalLink className="w-4 h-4" />
          </a>
        </>
      ) : (
        <>
          <p className="text-sm text-slate-400 mb-6 flex-1 blur-[3px] select-none">
            {s.description}
          </p>
          <Link
            to="/register"
            className="w-full py-2 bg-slate-900 text-white font-semibold rounded-xl text-center hover:bg-slate-800 transition-all flex items-center justify-center gap-2"
          >
            <Lock className="w-4 h-4" /> Unlock Full Access
          </Link>
        </>
      )}
    </div>
  );
};

export default ScholarshipCard;
