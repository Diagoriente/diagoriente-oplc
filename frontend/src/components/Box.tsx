import React from 'react';

export const Box: React.FC = props => {
  return (
    <div className="m-1 p-4 border-4 rounded border-slate-200">
      {props.children}
    </div>
  );
}

export default Box;
