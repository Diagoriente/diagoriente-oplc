import React from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {ExperienceId} from 'utils/helpers/Experiences';
import {JobRecommendation} from 'utils/helpers/Jobs';
import {} from 'ramda';

export const JobList: React.FC<{
    experiences: ExperienceId[] | undefined
    }> = ({
    experiences
    }) => {
  const [jobsRecommendation] = useFromBackend<JobRecommendation>(
    "job_recommendation",
    {
      experiences: experiences
    },
    [experiences],
    (r: any) => r as JobRecommendation,
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
            jobsRecommendation?.scores.map(({job, score}) =>
              <tr key={job.id} className="table-row">
                <td className="px-2 table-cell text-right">{
                  score.toLocaleString(undefined, {
                      minimumFractionDigits: 3,
                      maximumFractionDigits: 3,
                  })
                }</td>
                <td className="px-2 table-cell">{job.name}</td>
              </tr>)
          }
        </tbody>
      </table>
    </Box>
  );
}

export default JobList;
