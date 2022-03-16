import React from 'react';

export const Box: React.FC = props => {
  return (
    <div className="m-1 p-4 rounded bg-white">
      {props.children}
    </div>
  );
}

export default Box;
