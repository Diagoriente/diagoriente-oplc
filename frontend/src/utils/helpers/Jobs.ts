import {Record, RecordOf} from 'immutable';

export type Job = RecordOf<{name: string}>;

export const Job = Record({name: ""});

export const lessThan = (c1: Job, c2: Job): number => 
  c1.name < c2.name ? -1 :
  c1.name === c2.name ? 0 :
  1;


export type JobRecommendation = RecordOf<{job: Job, score: number}>

export const JobRecommendation = Record({job: Job(), score: 0})

export const lessThanScore = (c1: JobRecommendation, c2: JobRecommendation): number => 
  c1.score < c2.score ? -1 :
  c1.score === c2.score ? 0 :
  1;


