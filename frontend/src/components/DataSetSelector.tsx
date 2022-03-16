import React, {useEffect} from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {DataSet, DataSets} from 'utils/helpers/DataSets';

const DataSetSelector: React.FC<{
    current: DataSet | undefined,
    onSelect: (dataSet: DataSet) => void}>
    = ({current, onSelect}) => {

  const [dataSets] = useFromBackend<DataSets>("data_sets", {}, [], 
    (r) => DataSets({
      default: DataSet({name: r.default}),
      datasets: r.datasets.map((name: string) => DataSet({name: name})),
    }));

  useEffect(() => {
      if(current === undefined && dataSets !== undefined && dataSets.default.name !== "") {
        onSelect(dataSets.default)
      }
    },
    [dataSets]
  );

  return (
    <Box>
      <div className="text-left">
        <label className="inline" htmlFor="data-set-select">Jeu de données :</label>
        <select 
          className="rounded bg-indigo-200"
          name="data-set-select"
          id="data-set-select"
          defaultValue={current?.name}
          value={current?.name}
          onChange={e => onSelect(DataSet({name: e.target.value}))}
        >
          {
            dataSets?.datasets.map((ds: DataSet) => {
              return <option key={ds.name} value={ds.name}>{ds.name}</option>
              }
            )
          }
        </select>
      </div>
    </Box>
  );
};

export default DataSetSelector;

