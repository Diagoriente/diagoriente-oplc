import React, {useState, useEffect} from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {OrderedSet} from 'immutable';
import {Experience} from 'utils/helpers/Experiences';

export const ExperienceSelector: React.FC<{
    selected: OrderedSet<Experience> | undefined,
    setSelected: (experiences: OrderedSet<Experience> | undefined) => void
    }> = ({
    selected,
    setSelected
    }) => {
  const [experiences] = useFromBackend<OrderedSet<Experience>>("experiences",
    {},
    [],
    (r: any) => OrderedSet<Experience>(r.map(Experience)));

  const [notSelected, setNotSelected] = useState<OrderedSet<Experience> | undefined>(undefined);

  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    if(selected === undefined && notSelected === undefined && experiences !== undefined) {
      setSelected(OrderedSet([]));
      setNotSelected(() => experiences);
    }
  },
  [experiences, selected, notSelected, setSelected, setNotSelected]);

  const select = (c: Experience) => {
    setSelected(selected === undefined ? OrderedSet([c])
                                       : OrderedSet([c]).union(selected));
    setNotSelected(notSelected?.delete(c));
  };

  const deselect = (c: Experience) => {
    setSelected(selected?.delete(c));
    setNotSelected(notSelected === undefined ? OrderedSet([c])
                                             : OrderedSet([c]).union(notSelected));
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
              selected?.filter((c: Experience) => ~c.name.indexOf(filter))
                .map((c: Experience) => 
                  <div className="flex flex-row space-x-1" key={c.name + c.exp_type}>
                    <input type="checkbox" id={"checkbox-experience-" + c.name} 
                      value={c.name}
                      onChange={() => deselect(c)}
                      checked/>
                    <label htmlFor={"checkbox-experience-" + c.name}>{c.name}</label>
                  </div>) 
            }
          </div>

          <div>
            {
              notSelected?.filter((c: Experience) => ~c.name.indexOf(filter))
                .map((c: Experience) =>
                  <div className="flex flex-row space-x-1" key={c.name + c.exp_type}>
                    <input type="checkbox" id={"checkbox-experience-" + c.name}
                      value={c.name}
                      onChange={() => select(c)}/>
                    <label htmlFor={"checkbox-experience-" + c.name}>{c.name}</label>
                  </div>)
            }
          </div>
        </div>
      </div>
    </Box>
  );
};

export default ExperienceSelector;

