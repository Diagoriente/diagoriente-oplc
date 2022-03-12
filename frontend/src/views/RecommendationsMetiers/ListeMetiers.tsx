import React from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {Metier, metier, lessThan} from 'utils/helpers/Metiers';
import {OrderedSet, fromJS} from 'immutable';

export const ListeMetiers: React.FC = () => {
  const [metiers] = useFromBackend<OrderedSet<Metier>>("metiers",
    {dataset: {name: "local test csv"}},
    [],
    (r: any[]) => {
      const res = OrderedSet(r.map(metier)).sort();
      return res;
    })

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
