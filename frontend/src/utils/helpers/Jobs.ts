
export type JobId = string;
export type Job = {name: string};

export const lessThan = (c1: Job, c2: Job): number => 
  c1.name < c2.name ? -1 :
  c1.name === c2.name ? 0 :
  1;


export type JobRecommendation = {
  scores: {job: {id: JobId, name: string}, score: number}[],
  graph: {
    edges: [JobId, JobId][],
    layout: Record<JobId, [number, number]>,
  },
};

