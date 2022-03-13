import React, {useState, useEffect} from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {OrderedSet} from 'immutable';
import {Competence, competence, lessThan} from 'utils/helpers/Competences';

export const CompetenceSelector: React.FC = () => {
  const [competences] = useFromBackend<OrderedSet<Competence>>("competences",
    {dataset: {name: "local test csv"}},
    [],
    (r: any) => OrderedSet<Competence>(r.competences.map(competence)).sort(lessThan));

  const [selected, setSelected] = useState<OrderedSet<Competence> | undefined>(undefined);
  const [notSelected, setNotSelected] = useState<OrderedSet<Competence> | undefined>(undefined);

  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    if(selected === undefined && notSelected === undefined && competences !== undefined) {
      setSelected(() => OrderedSet([]));
      setNotSelected(() => OrderedSet(competences).sort(lessThan));
    }
  },
  [competences, setSelected, setNotSelected]);

  const select = (c: Competence) => {
    setSelected(selected?.add(c).sort(lessThan));
    setNotSelected(notSelected?.delete(c));
  };

  const deselect = (c: Competence) => {
    setSelected(selected?.delete(c));
    setNotSelected(notSelected?.add(c).sort(lessThan));
  };

  return (
    <Box>
      <div className="flex flex-col">

        <label className="font-bold underline" htmlFor="competences-search">
          Sélectionnez des compétences :
        </label>

        <input className="border rounded px-1" type="text" 
          id="competences-search" name="competences-search"
          placeholder="Tapez ici pour filtrer les compétences"
          onChange={e => setFilter(e.currentTarget.value)}/>

        <div className="divide-y-2">
          <div>
            { 
              selected?.filter((c: Competence) => ~c.name.indexOf(filter))
                .map((c: Competence) => 
                  <div className="flex flex-row space-x-1" key={c.name}>
                    <input type="checkbox" id={"checkbox-competence-" + c.name} 
                      value={c.name}
                      onChange={() => deselect(c)}
                      checked/>
                    <label htmlFor={"checkbox-competence-" + c.name}>{c.name}</label>
                  </div>) 
            }
          </div>

          <div>
            {
              notSelected?.filter((c: Competence) => ~c.name.indexOf(filter))
                .map((c: Competence) =>
                  <div className="flex flex-row space-x-1" key={c.name}>
                    <input type="checkbox" id={"checkbox-competence-" + c.name}
                      value={c.name}
                      onChange={() => select(c)}/>
                    <label htmlFor={"checkbox-competence-" + c.name}>{c.name}</label>
                  </div>)
            }
          </div>
        </div>
      </div>
    </Box>
  );
};

export default CompetenceSelector;

