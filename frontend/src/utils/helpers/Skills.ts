import {Record, RecordOf} from 'immutable';

export type Skill = RecordOf<{name: string}>;

export const Skill = Record({name: ""});

export const lessThan = (c1: Skill, c2: Skill): number => 
  c1.name < c2.name ? -1 :
  c1.name === c2.name ? 0 :
  1;
