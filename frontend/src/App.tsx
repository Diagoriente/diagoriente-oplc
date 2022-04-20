import React from 'react';
import './App.css';
import {JobRecommendation} from './views/JobRecommendation/JobRecommendation';

function App() {
  return (
    <div className="App bg-gray-100">
      <header className="App-header">
        <JobRecommendation/>
      </header>
    </div>
  );
}

export default App;
