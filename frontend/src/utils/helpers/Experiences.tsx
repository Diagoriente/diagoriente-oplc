import {Record, RecordOf} from 'immutable';

export type Experience = RecordOf<{name: string, exp_type: string}>;

export const Experience = Record({name: "", exp_type: ""});

