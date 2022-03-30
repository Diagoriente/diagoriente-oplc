import React, {useState, useEffect} from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import * as R from 'ramda';
import {Experience, ExperienceId} from 'utils/helpers/Experiences';

export const ExperienceSelector: React.FC<{
    selected: ExperienceId[] | undefined,
    setSelected: (experiences: ExperienceId[] | undefined) => void
    }> = ({
    selected,
    setSelected
    }) => {
  const [experiences] = useFromBackend<Record<ExperienceId, Experience>>("experiences",
    {},
    [],
    (r: any) => r as Record<ExperienceId, Experience>);

  const [notSelected, setNotSelected] = useState<ExperienceId[] | undefined>(undefined);

  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    if(selected === undefined && notSelected === undefined && experiences !== undefined) {
      setSelected([]);
      setNotSelected(() => R.keys(experiences));
    }
  },
  [experiences, selected, notSelected, setSelected, setNotSelected]);

  const select = (c: ExperienceId) => {
    setSelected(selected === undefined ? [c] : R.append(c, selected));
    setNotSelected(notSelected === undefined
                   ? []
                   : R.remove(R.findIndex(R.equals(c), notSelected), 1, notSelected));
  };

  const deselect = (c: ExperienceId) => {
    setSelected(selected === undefined
                ? [] :
                R.remove(R.findIndex(R.equals(c), selected), 1, selected));
    setNotSelected(notSelected === undefined ? [c] : R.append(c, notSelected));
  };

  return (
    <Box>
      <div className="flex flex-col">

        <label 
          className="font-bold underline text-center" 
          htmlFor="experiences-search">
          Sélectionnez des expériences :
        </label>

        <input className="border rounded px-1" type="text" 
          id="experiences-search" name="experiences-search"
          placeholder="Tapez ici pour filtrer les expériences"
          onChange={e => setFilter(e.currentTarget.value)}/>

        <div className="divide-y-2">
          <div>
            { 
              selected
                ?.map((e: ExperienceId) => {
                  const exp = experiences?.[e];
                  if(exp === undefined) {
                    throw new ReferenceError(`Could not find any experience with id ${e}.`);
                  }
                  return {e: e, exp: exp};
                  })
                .filter(({exp}: {e: ExperienceId, exp: Experience}) =>
                  ~exp.name.indexOf(filter))
                .map(({e, exp}: {e: ExperienceId, exp: Experience}) => 
                  <div className="flex flex-row space-x-1" key={e}>
                    <input type="checkbox" id={"checkbox-experience-" + exp.name} 
                      value={exp.name}
                      onChange={() => deselect(e)}
                      checked/>
                    <label htmlFor={"checkbox-experience-" + exp.name}>{exp.name}</label>
                  </div>) 
            }
          </div>

          <div>
            {
              notSelected
                ?.map((e: ExperienceId) => {
                  const exp = experiences?.[e];
                  if(exp === undefined) {
                    throw new ReferenceError(`Could not find any experience with id ${e}.`);
                  }
                  return {e: e, exp: exp};
                  })
                .filter(({exp}: {e: ExperienceId, exp: Experience}) => {
                  return ~exp.name.indexOf(filter);
                  })
                .map(({e, exp}: {e: ExperienceId, exp: Experience}) =>
                  <div className="flex flex-row space-x-1" key={e}>
                    <input type="checkbox" id={"checkbox-experience-" + exp.name}
                      value={exp.name}
                      onChange={() => select(e)}/>
                    <label htmlFor={"checkbox-experience-" + exp.name}>{exp.name}</label>
                  </div>)
            }
          </div>
        </div>
      </div>
    </Box>
  );
};

export default ExperienceSelector;

