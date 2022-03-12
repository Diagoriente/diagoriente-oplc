import React, {useState} from 'react';
import DataSetSelector from 'components/DataSetSelector';
import ListeMetiers from './ListeMetiers';
import CompetenceSelector from './CompetenceSelector';
import {DataSet} from 'utils/helpers/DataSets';
import useStateSP from 'hooks/useStateSP';

export const RecommendationsMetiers: React.FC = () => {
  const [dataSet, setDataSet] = useState<DataSet | undefined>(undefined);
    //useStateSP<DataSet | undefined>(undefined, "data_set", 
    //  (s: string | null) => s === null ? null : DataSet({name: s}),
    //  (ds: DataSet | undefined) => ds === undefined ? null : ds.name);

  return (
    <div className="flex flex-col">
      <DataSetSelector current={dataSet} onSelect={setDataSet}/>
      <div className="flex flex-row">
        <CompetenceSelector/>
        <ListeMetiers/>
      </div>
    </div>
  );
}
