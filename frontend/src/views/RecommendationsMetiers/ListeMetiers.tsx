import React from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {Metier, metier, lessThan} from 'utils/helpers/Metiers';
import {OrderedSet, fromJS} from 'immutable';
import {DataSet} from 'utils/helpers/DataSets';

export const ListeMetiers: React.FC<{dataSet: DataSet}> = ({dataSet}) => {
  const [metiers] = useFromBackend<OrderedSet<Metier>>("metiers",
    {dataset: dataSet},
    [],
    (r: any) => OrderedSet<Metier>(r.metiers.map(metier)).sort())

  return (
    <Box>
      <p className="font-bold underline">
        Métiers recommandés :
      </p>
      <ul>
        {metiers?.map((m) => <li key={m.name}>{m.name}</li>)}
      </ul>
    </Box>
  );
}

export default ListeMetiers;
