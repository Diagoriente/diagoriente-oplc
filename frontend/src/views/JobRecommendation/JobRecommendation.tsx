import React, {useState} from 'react';
import useFromBackend from 'hooks/useFromBackend';
import {JobRecommendation as JobRecommendationT} from 'utils/helpers/Jobs';
import JobList from './JobList';
import ExperienceSelector from './ExperienceSelector';
import {ExperienceId} from 'utils/helpers/Experiences';
import SkillGraphView from './SkillGraphView';

export const JobRecommendation: React.FC = () => {
  const [selectedExperiences, setSelectedExperiences] = useState<ExperienceId[] | undefined>(undefined);
  const [jobRecommendation] = useFromBackend<JobRecommendationT>(
      "job_recommendation",
      {
        experiences: selectedExperiences,
        return_graph: true,
      },
      [selectedExperiences],
      (r: any) => r as JobRecommendationT,
    )

  return (
    <div className="h-screen flex flex-col">
      <div className="h-full flex flex-row">
        <div className="h-full overflow-auto w-1/2">
          <ExperienceSelector
            selected={selectedExperiences}
            setSelected={setSelectedExperiences}
          />
        </div>
        <div className="h-full w-1/2 flex flex-col">
          <div className="h-1/2">
            <SkillGraphView
              jobRecommendation={jobRecommendation}
              />
          </div>
          <div className="h-1/2 overflow-auto">
            <JobList
              jobRecommendation={jobRecommendation}
              />
          </div>
        </div>
      </div>
    </div>
  );
}
