import React, { useState } from 'react';
import './App.css';
import AudioUpload from './components/AudioUpload';
import SoapViewer from './components/SoapViewer';

function App() {
  const [soap, setSoap] = useState('');

  return (
    <div className="App">
      <h1>PhysioSOAP Generator</h1>
      <AudioUpload onResult={setSoap} />
      <SoapViewer soap={soap} />
    </div>
  );
}

export default App;
