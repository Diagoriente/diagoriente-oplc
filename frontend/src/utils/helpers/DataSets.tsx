import {Record, RecordOf} from 'immutable';

export type DataSet = RecordOf<{name: string}>;
export const DataSet = Record({name: ""});

export type DataSets = RecordOf<{default: DataSet, datasets: DataSet[]}>;
export const DataSets = Record({default: DataSet(), datasets: [DataSet()]});

