import React, {useState} from 'react';
import DataSetSelector from 'components/DataSetSelector';
import ListeMetiers from './ListeMetiers';
import CompetenceSelector from './CompetenceSelector';
import {DataSet} from 'utils/helpers/DataSets';
import {Competence} from 'utils/helpers/Competences';
import {OrderedSet} from 'immutable';

export const RecommendationsMetiers: React.FC = () => {
  const [dataSet, setDataSet] = useState<DataSet | undefined>(undefined);
  const [selectedCompetences, setSelectedCompetences] = useState<OrderedSet<Competence> | undefined>(undefined);
    //useStateSP<DataSet | undefined>(undefined, "data_set", 
    //  (s: string | null) => s === null ? null : DataSet({name: s}),
    //  (ds: DataSet | undefined) => ds === undefined ? null : ds.name);

  return (
    <div className="flex flex-col">
      <DataSetSelector current={dataSet} onSelect={setDataSet}/>
      <div className="flex flex-row">
        { dataSet === undefined ? <></> :
          <>
            <div className="w-1/2">
              <CompetenceSelector
                dataSet={dataSet}
                selected={selectedCompetences}
                setSelected={setSelectedCompetences} />
            </div>
            <div className="w-1/2">
            <ListeMetiers dataSet={dataSet} competences={selectedCompetences}/>
            </div>
          </>
        }
      </div>
    </div>
  );
}
