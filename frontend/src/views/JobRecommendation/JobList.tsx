import React from 'react';
import Box from 'components/Box';
import {JobRecommendation} from 'utils/helpers/Jobs';

export const JobList: React.FC<{
    jobRecommendation?: JobRecommendation
    }> = ({
    jobRecommendation
    }) => {
  

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
            jobRecommendation?.scores.map(({job, score}) =>
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
