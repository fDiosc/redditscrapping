import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ClerkAuthProvider } from './components/ClerkAuthProvider'
import './index.css'
import App from './App.jsx'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', background: '#09090b', color: '#ff4444', minHeight: '100vh', fontFamily: 'monospace' }}>
          <h1>SonarPro strictly halted.</h1>
          <p>{this.state.error?.toString()}</p>
          <pre style={{ color: '#888', fontSize: '12px' }}>Check the browser console for details.</pre>
          <button onClick={() => window.location.reload()} style={{ background: '#6366f1', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer' }}>Reload Application</button>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <ClerkAuthProvider>
          <App />
        </ClerkAuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
