import {Record, RecordOf} from 'immutable';

export type Competence = RecordOf<{name: string}>;

export const competence = Record({name: ""});

export const lessThan = (c1: Competence, c2: Competence): number => 
  c1.name < c2.name ? -1 :
  c1.name == c2.name ? 0 :
  1;
