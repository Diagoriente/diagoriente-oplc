import React, {useState, useEffect} from 'react';
import useFromBackend from 'hooks/useFromBackend';
import Box from 'components/Box';
import {OrderedSet} from 'immutable';
import {Competence, lessThan} from 'utils/helpers/Competences';
import {DataSet} from 'utils/helpers/DataSets';

export const CompetenceSelector: React.FC<{
    dataSet: DataSet,
    selected: OrderedSet<Competence> | undefined,
    setSelected: (competences: OrderedSet<Competence> | undefined) => void
    }> = ({
    dataSet,
    selected,
    setSelected
    }) => {
  const [competences] = useFromBackend<OrderedSet<Competence>>("competences",
    {dataset: dataSet},
    [],
    (r: any) => OrderedSet<Competence>(r.map(Competence)));

  const [notSelected, setNotSelected] = useState<OrderedSet<Competence> | undefined>(undefined);

  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    if(selected === undefined && notSelected === undefined && competences !== undefined) {
      setSelected(OrderedSet([]));
      setNotSelected(() => competences);
    }
  },
  [competences, selected, notSelected, setSelected, setNotSelected]);

  const select = (c: Competence) => {
    setSelected(selected === undefined ? OrderedSet([c])
                                       : OrderedSet([c]).union(selected));
    setNotSelected(notSelected?.delete(c));
  };

  const deselect = (c: Competence) => {
    setSelected(selected?.delete(c));
    setNotSelected(notSelected === undefined ? OrderedSet([c])
                                             : OrderedSet([c]).union(notSelected));
  };

  return (
    <Box>
      <div className="flex flex-col">

        <label 
          className="font-bold underline text-center" 
          htmlFor="competences-search">
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

