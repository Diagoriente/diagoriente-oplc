import {Record, RecordOf} from 'immutable';

export type Metier = RecordOf<{name: string}>;

export const Metier = Record({name: ""});

export const lessThan = (c1: Metier, c2: Metier): number => 
  c1.name < c2.name ? -1 :
  c1.name === c2.name ? 0 :
  1;


export type MetierSuggestion = RecordOf<{metier: Metier, score: number}>

export const MetierSuggestion = Record({metier: Metier(), score: 0})

export const lessThanScore = (c1: MetierSuggestion, c2: MetierSuggestion): number => 
  c1.score < c2.score ? -1 :
  c1.score === c2.score ? 0 :
  1;


