import React from 'react';

const SoapViewer: React.FC<{ soap: string }> = ({ soap }) => {
  if (!soap) return null;

  return (
    <div>
      <h2>Generated SOAP Note</h2>
      <pre style={{ whiteSpace: 'pre-wrap' }}>{soap}</pre>
    </div>
  );
};

export default SoapViewer;
