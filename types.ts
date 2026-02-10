
export interface Scholarship {
  id: string;
  title: string;
  country: string;
  deadline: string;
  funding: 'Full' | 'Partial' | 'Tuition Only';
  degree: 'Masters' | 'PhD' | 'PostDoc';
  description: string;
  link: string;
  addedAt: number;
}

export interface UserProfile {
  name: string;
  email: string;
  major: string;
  degreeTarget: string;
  points: number;
  activityHistory: { date: number; action: string }[];
}

export interface GroundingChunk {
  web?: {
    uri: string;
    title: string;
  };
}
