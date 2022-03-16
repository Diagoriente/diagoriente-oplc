import React from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {Competence} from 'utils/helpers/Competences';
import {MetierSuggestion} from 'utils/helpers/Metiers';
import {OrderedSet} from 'immutable';
import {DataSet} from 'utils/helpers/DataSets';

export const ListeMetiers: React.FC<{
    dataSet: DataSet, 
    competences: OrderedSet<Competence> | undefined
    }> = ({
    dataSet,
    competences
    }) => {
  const [metiersSuggestion] = useFromBackend<OrderedSet<MetierSuggestion>>(
    "metiers_suggestion",
    {
      dataset: dataSet,
      competences: competences
    },
    [dataSet, competences],
    (r: any) => (
      OrderedSet<MetierSuggestion>(r.scores.map(MetierSuggestion))
    )
  )

  return (
    <Box>
      <p className="font-bold underline text-center">
        Métiers recommandés :
      </p>
      <table className="table">
        <thead className="table-header-group bg-gray-50">
          <tr className="table-row">
            <th className="px-2 table-cell font-bold text-center">Score</th>
            <th className="px-2 table-cell font-bold text-left">Intitulé</th>
          </tr>
        </thead>
        <tbody className="table-header-group ">
          {
            metiersSuggestion?.map((m) =>
              <tr key={m.metier.name} className="table-row">
                <td className="px-2 table-cell text-right">{m.score}</td>
                <td className="px-2 table-cell">{m.metier.name}</td>
              </tr>)
          }
        </tbody>
      </table>
    </Box>
  );
}

export default ListeMetiers;
