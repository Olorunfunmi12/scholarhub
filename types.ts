
export interface Scholarship {
  id: string;
  title: string;
  country: string;
  region: string;
  university: string;
  deadline: string;
  funding: 'Full' | 'Partial' | 'Tuition Only';
  degree: 'Masters' | 'PhD' | 'PostDoc';
  field: string;
  description: string;
  link: string;
  addedAt: number;
}

export interface Account {
  name: string;
  email: string;
  country: string;
  degreeTarget: string;
  token: string;
  createdAt: number;
}

export interface GroundingChunk {
  web?: {
    uri: string;
    title: string;
  };
}
