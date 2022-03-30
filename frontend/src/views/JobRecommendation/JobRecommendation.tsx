import React, {useState} from 'react';
import JobList from './JobList';
import ExperienceSelector from './ExperienceSelector';
import {ExperienceId} from 'utils/helpers/Experiences';

export const JobRecommendation: React.FC = () => {
  const [selectedExperiences, setSelectedExperiences] = useState<ExperienceId[] | undefined>(undefined);

  return (
    <div className="flex flex-col">
      <div className="flex flex-row">
        {
          <>
            <div className="w-1/2">
              <ExperienceSelector
                selected={selectedExperiences
             }
                setSelected={setSelectedExperiences
             } />
            </div>
            <div className="w-1/2">
            <JobList experiences={selectedExperiences}/>
            </div>
          </>
        }
      </div>
    </div>
  );
}
