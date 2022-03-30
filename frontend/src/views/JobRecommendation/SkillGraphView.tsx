import React from 'react';
import useFromBackend from 'hooks/useFromBackend';
import {JobRecommendation} from 'utils/helpers/Jobs';
import {SkillId, Skill} from 'utils/helpers/Skills';
import Box from 'components/Box';
import * as R from 'ramda';
import * as d3 from 'd3';


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

  var skillGraphView = undefined;

  if (jobRecommendation !== undefined) {
    const circleRadius=0.02

    const xScale = d3.scaleLinear();
    xScale.domain([-1, 1]);
    xScale.range([0 + circleRadius, 1 - circleRadius]);

    const yScale = d3.scaleLinear()
    yScale.domain([-1, 1 + circleRadius]);
    yScale.range([0 + circleRadius, 1 - circleRadius]);

    const centralityExtent = d3.extent(R.map(({score}) => score,
                                       jobRecommendation.scores)
                                       )

    const colorScale = d3.scaleSequential()
    colorScale.domain(centralityExtent[0] === undefined ? [1, 1] : centralityExtent);
    colorScale.range([0, 0.1]);
    colorScale.clamp(true);
    colorScale.interpolator(d3.interpolateGnBu);

    skillGraphView = (
        <div id="skill-graph-view" className="h-full w-full">
          <svg className="h-full w-full" viewBox="0 0 1 1">
            {R.map(([u, v]: [SkillId, SkillId]) =>
                   <line
                    key={`${u}-${v}`}
                    x1={xScale(jobRecommendation.skill_graph.layout[u][0])}
                    y1={yScale(jobRecommendation.skill_graph.layout[u][1])}
                    x2={xScale(jobRecommendation.skill_graph.layout[v][0])}
                    y2={yScale(jobRecommendation.skill_graph.layout[v][1])}
                    strokeWidth={circleRadius / 10}
                    stroke="steelblue"
                   />,
              jobRecommendation.skill_graph.edges,
              )
            }
            {Object.entries(R.mapObjIndexed(
             (coords, skillId) =>
                <g>
                  <circle
                    key={skillId}
                    cx={xScale(coords[0])}
                    cy={yScale(coords[1])}
                    r={circleRadius}
                    fill={`${colorScale(jobRecommendation.skill_graph.centrality[skillId])}`}
                  />
                  <text
                    key={`skill-name-${skillId}`}
                    x={xScale(coords[0])}
                    y={yScale(coords[1])}
                    fontSize="0.2%"
                    fill="black"
                  >
                    {skills?.[skillId].name}
                  </text>
                </g>,
             jobRecommendation.skill_graph.layout,
             ))
             }
          </svg>
        </div>
    );
  }

  return (
    <Box>
        <p className="h-1/6 font-bold underline text-center">
          Réseau des compétences :
        </p>
        <div className="h-5/6">
          {skillGraphView}
        </div>
    </Box>
  );
}

export default SkillGraphView;
