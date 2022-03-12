import {Record, RecordOf} from 'immutable';

export type Metier = RecordOf<{name: string}>;

export const metier = Record({name: ""});

export const lessThan = (c1: Metier, c2: Metier): number => 
  c1.name < c2.name ? -1 :
  c1.name === c2.name ? 0 :
  1;

