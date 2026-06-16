
import { Scholarship } from '../types';

export const scholarships: Scholarship[] = [
  {
    id: '1', title: 'Chevening Scholarship', country: 'United Kingdom', region: 'Europe',
    university: 'Any UK University', deadline: 'Nov 5, 2026', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'Fully funded UK government award covering tuition, a monthly stipend, flights, and an arrival allowance for future global leaders.',
    link: 'https://www.chevening.org/apply/', addedAt: Date.now(),
  },
  {
    id: '2', title: 'DAAD EPOS Scholarship', country: 'Germany', region: 'Europe',
    university: 'Various', deadline: 'Oct 31, 2026', funding: 'Full', degree: 'Masters',
    field: 'Development & Public Policy', description: 'Development-related postgraduate scholarship covering tuition, monthly stipend, travel allowance, and health insurance.',
    link: 'https://www.daad.de/en/', addedAt: Date.now(),
  },
  {
    id: '3', title: 'Fulbright Foreign Student Program', country: 'United States', region: 'North America',
    university: 'Various', deadline: 'Feb 2026', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'Flagship U.S. government program funding tuition, living stipend, airfare, and health insurance for graduate study.',
    link: 'https://foreign.fulbrightonline.org/', addedAt: Date.now(),
  },
  {
    id: '4', title: 'Vanier Canada Graduate Scholarship', country: 'Canada', region: 'North America',
    university: 'Canadian Universities', deadline: 'Nov 3, 2026', funding: 'Full', degree: 'PhD',
    field: 'Any Field', description: 'CAD $50,000 per year for three years to doctoral students demonstrating leadership and academic excellence.',
    link: 'https://vanier.gc.ca/', addedAt: Date.now(),
  },
  {
    id: '5', title: 'Australian National University Chancellor\'s International Scholarship', country: 'Australia', region: 'Oceania',
    university: 'ANU', deadline: 'Aug 31, 2026', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'Full tuition fee waiver plus living stipend for high-achieving international students.',
    link: 'https://www.anu.edu.au/study/scholarships', addedAt: Date.now(),
  },
  {
    id: '6', title: 'Erasmus Mundus Joint Master Degrees', country: 'European Union', region: 'Europe',
    university: 'Consortium of EU Universities', deadline: 'Jan 15, 2027', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'Study across multiple European countries with full tuition coverage, travel costs, and a monthly living allowance.',
    link: 'https://www.eacea.ec.europa.eu/scholarships/', addedAt: Date.now(),
  },
  {
    id: '7', title: 'Swiss Government Excellence Scholarship', country: 'Switzerland', region: 'Europe',
    university: 'Various', deadline: 'Dec 2026', funding: 'Full', degree: 'PhD',
    field: 'Any Field', description: 'Monthly stipend, tuition waiver, and health insurance for doctoral and postdoctoral research in Switzerland.',
    link: 'https://www.sbfi.admin.ch/scholarships', addedAt: Date.now(),
  },
  {
    id: '8', title: 'MEXT Japanese Government Scholarship', country: 'Japan', region: 'Asia',
    university: 'Various', deadline: 'May 2027', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'Covers tuition, a monthly allowance, and round-trip airfare for graduate study at Japanese universities.',
    link: 'https://www.studyinjapan.go.jp/en/', addedAt: Date.now(),
  },
  {
    id: '9', title: 'Holland Scholarship', country: 'Netherlands', region: 'Europe',
    university: 'Dutch Research Universities', deadline: 'May 1, 2027', funding: 'Partial', degree: 'Masters',
    field: 'Any Field', description: 'EUR 5,000 one-time grant for non-EEA students starting a Bachelor\'s or Master\'s in the Netherlands.',
    link: 'https://www.studyinholland.nl/finances/holland-scholarship', addedAt: Date.now(),
  },
  {
    id: '10', title: 'Singapore International Graduate Award (SINGA)', country: 'Singapore', region: 'Asia',
    university: 'A*STAR / NUS / NTU', deadline: 'Dec 1, 2026', funding: 'Full', degree: 'PhD',
    field: 'Science & Engineering', description: 'Monthly stipend, tuition coverage, airfare, and a one-time settling-in allowance for PhD research.',
    link: 'https://www.a-star.edu.sg/singa', addedAt: Date.now(),
  },
  {
    id: '11', title: 'New Zealand International Doctoral Research Scholarship', country: 'New Zealand', region: 'Oceania',
    university: 'NZ Universities', deadline: 'Varies', funding: 'Full', degree: 'PhD',
    field: 'Any Field', description: 'Full tuition waiver plus a living stipend of NZD $27,000+ per year for three years.',
    link: 'https://www.education.govt.nz/', addedAt: Date.now(),
  },
  {
    id: '12', title: 'Eiffel Excellence Scholarship', country: 'France', region: 'Europe',
    university: 'Various', deadline: 'Jan 2027', funding: 'Full', degree: 'Masters',
    field: 'Engineering, Economics, Law', description: 'Monthly allowance, travel costs, and health insurance for outstanding international students.',
    link: 'https://www.campusfrance.org/en/eiffel-scholarship-program-of-excellence', addedAt: Date.now(),
  },
  {
    id: '13', title: 'Korean Government Scholarship Program (GKS)', country: 'South Korea', region: 'Asia',
    university: 'Various', deadline: 'Feb 2027', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'Tuition, monthly stipend, settlement allowance, airfare, and Korean language training included.',
    link: 'https://www.studyinkorea.go.kr/', addedAt: Date.now(),
  },
  {
    id: '14', title: 'Chinese Government Scholarship (CSC)', country: 'China', region: 'Asia',
    university: 'Various', deadline: 'Apr 2027', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'Full tuition, accommodation, monthly stipend, and comprehensive medical insurance.',
    link: 'https://www.campuschina.org/', addedAt: Date.now(),
  },
  {
    id: '15', title: 'Norwegian Quota Scheme', country: 'Norway', region: 'Europe',
    university: 'Norwegian Universities', deadline: 'Dec 1, 2026', funding: 'Tuition Only', degree: 'Masters',
    field: 'Any Field', description: 'No tuition fees at Norwegian public universities; living costs supported through partner agreements.',
    link: 'https://www.studyinnorway.no/', addedAt: Date.now(),
  },
  {
    id: '16', title: 'VLIR-UOS Scholarships', country: 'Belgium', region: 'Europe',
    university: 'Flemish Universities', deadline: 'Jan 2027', funding: 'Full', degree: 'Masters',
    field: 'Development Studies', description: 'Full scholarship covering tuition, living allowance, insurance, and travel for students from developing countries.',
    link: 'https://www.vliruos.be/', addedAt: Date.now(),
  },
  {
    id: '17', title: 'Swedish Institute Scholarships for Global Professionals', country: 'Sweden', region: 'Europe',
    university: 'Various', deadline: 'Feb 2027', funding: 'Full', degree: 'Masters',
    field: 'Leadership & Sustainability', description: 'Full tuition, living allowance, travel grant, and insurance for future global leaders.',
    link: 'https://si.se/en/apply/scholarships/', addedAt: Date.now(),
  },
  {
    id: '18', title: 'Invest Your Talent in Italy', country: 'Italy', region: 'Europe',
    university: 'Various', deadline: 'Jun 2027', funding: 'Partial', degree: 'Masters',
    field: 'Engineering, Economics, Design', description: 'Tuition waiver and internship placement with Italian companies for international students.',
    link: 'https://www.investyourtalentinitaly.uniroma2.it/', addedAt: Date.now(),
  },
  {
    id: '19', title: 'Government of Ireland International Scholarships', country: 'Ireland', region: 'Europe',
    university: 'Irish Universities', deadline: 'Mar 2027', funding: 'Full', degree: 'Masters',
    field: 'Any Field', description: 'EUR 10,000 tuition contribution plus a one-year non-EU student visa support package.',
    link: 'https://hea.ie/policy/access-policy/international-scholarships/', addedAt: Date.now(),
  },
  {
    id: '20', title: 'Rhodes Scholarship', country: 'United Kingdom', region: 'Europe',
    university: 'University of Oxford', deadline: 'Oct 2026', funding: 'Full', degree: 'PhD',
    field: 'Any Field', description: 'One of the oldest and most prestigious international postgraduate awards, fully funding study at Oxford.',
    link: 'https://www.rhodeshouse.ox.ac.uk/', addedAt: Date.now(),
  },
  {
    id: '21', title: 'Knight-Hennessy Scholars', country: 'United States', region: 'North America',
    university: 'Stanford University', deadline: 'Oct 2026', funding: 'Full', degree: 'PhD',
    field: 'Any Field', description: 'Full funding for any graduate program at Stanford plus leadership development programming.',
    link: 'https://knight-hennessy.stanford.edu/', addedAt: Date.now(),
  },
  {
    id: '22', title: 'Commonwealth Scholarships', country: 'United Kingdom', region: 'Europe',
    university: 'Various', deadline: 'Dec 2026', funding: 'Full', degree: 'Masters',
    field: 'Development-related Subjects', description: 'Funded by UK aid, covering tuition, airfare, stipend, and thesis grants for Commonwealth citizens.',
    link: 'https://cscuk.fcdo.gov.uk/', addedAt: Date.now(),
  },
  {
    id: '23', title: 'Gates Cambridge Scholarship', country: 'United Kingdom', region: 'Europe',
    university: 'University of Cambridge', deadline: 'Dec 2026', funding: 'Full', degree: 'PhD',
    field: 'Any Field', description: 'Full-cost scholarship for outstanding applicants from outside the UK to pursue postgraduate study at Cambridge.',
    link: 'https://www.gatescambridge.org/', addedAt: Date.now(),
  },
  {
    id: '24', title: 'Endeavour Leadership Program', country: 'Australia', region: 'Oceania',
    university: 'Various', deadline: 'Varies', funding: 'Full', degree: 'PhD',
    field: 'Any Field', description: 'Tuition, travel, establishment allowance, and a monthly stipend for international postgraduate researchers.',
    link: 'https://www.education.gov.au/endeavour-leadership-program', addedAt: Date.now(),
  },
];

export const COUNTRIES = Array.from(new Set(scholarships.map(s => s.country))).sort();
export const DEGREES = ['Masters', 'PhD', 'PostDoc'] as const;
export const FUNDING_TYPES = ['Full', 'Partial', 'Tuition Only'] as const;
