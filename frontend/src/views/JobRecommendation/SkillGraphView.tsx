import React, {useEffect} from 'react';
import useFromBackend from 'hooks/useFromBackend';
import {JobRecommendation} from 'utils/helpers/Jobs';
import {SkillId, Skill} from 'utils/helpers/Skills';
import Box from 'components/Box';
import {skillGraphViz} from 'oplc-graph-vis';

const SkillGraphView: React.FC<{
    jobRecommendation?: JobRecommendation
    }> = ({
    jobRecommendation
    }) => {

  const [skills] = useFromBackend<Record<SkillId, Skill>>(
      "skills",
      {},
      [],
      (r: any) => r as Record<SkillId, Skill>,
    )

  useEffect(() => {
      if (jobRecommendation !== undefined && skills !== undefined) {
        skillGraphViz(
          jobRecommendation,
          skills,
          "skill-graph-viz",
          "zoom-in",
          "zoom-out",
        );
      }

      return () => {
        const container = document.getElementById("skill-graph-viz")
        if (container !== undefined && container !== null) {
          container.innerHTML = "";
        }
      };
    },
    [jobRecommendation, skills],
  );

  return (
    <Box>
        <p className="h-1/6 font-bold underline text-center">
          Réseau des compétences :
        </p>
        <div className="relative w-full h-full">
          <div
            id="skill-graph-viz"
            className="w-full h-full">
          </div>
          <div
              id="controls"
              className="absolute left-0 top-0">
            <button 
              id="zoom-in"
              type="button"
              className="w-8 h-8 border-2 rounded-md"
              >
              +
            </button>
            <button 
              id="zoom-out"
              type="button"
              className="w-8 h-8 border-2 rounded-md"
              >
              -
            </button>
          </div>
        </div>
    </Box>
  );
}

export default SkillGraphView;
