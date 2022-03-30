export type SkillId = string;
export type Skill = {name: string};

export const lessThan = (c1: Skill, c2: Skill): number =>
  c1.name < c2.name ? -1 :
  c1.name === c2.name ? 0 :
  1;
