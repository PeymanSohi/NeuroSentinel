import React from 'react';

function App() {
  return (
    <div style={{ 
      backgroundColor: '#0f172a', 
      color: 'white', 
      minHeight: '100vh',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>NeuroSentinel Dashboard</h1>
      <p>Welcome to the distributed cyber defense platform dashboard.</p>
      <div style={{ 
        backgroundColor: '#1e293b', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>System Status</h2>
        <p>✅ Dashboard is working!</p>
        <p>✅ React is loading correctly</p>
        <p>✅ Basic styling is applied</p>
      </div>
    </div>
  );
}

export default App;
