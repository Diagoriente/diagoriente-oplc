import React from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {Experience} from 'utils/helpers/Experiences';
import {JobRecommendation} from 'utils/helpers/Jobs';
import {OrderedSet} from 'immutable';

export const JobList: React.FC<{
    experiences: OrderedSet<Experience> | undefined
    }> = ({
    experiences
    }) => {
  const [jobsRecommendation] = useFromBackend<JobRecommendation[]>(
    "jobs_recommendation",
    {
      experiences: experiences
    },
    [experiences],
    (r: any) => r.scores.map(JobRecommendation),
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
            jobsRecommendation?.map((m) =>
              <tr key={m.job.name} className="table-row">
                <td className="px-2 table-cell text-right">{m.score}</td>
                <td className="px-2 table-cell">{m.job.name}</td>
              </tr>)
          }
        </tbody>
      </table>
    </Box>
  );
}

export default JobList;
