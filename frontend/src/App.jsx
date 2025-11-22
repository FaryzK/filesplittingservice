import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Inference from './pages/Inference';
import Model from './pages/Model';
import './App.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="navigation">
      <div className="nav-container">
        <h1 className="nav-title">Document Splitter</h1>
        <div className="nav-links">
          <Link
            to="/"
            className={location.pathname === '/' ? 'active' : ''}
          >
            Inference
          </Link>
          <Link
            to="/model"
            className={location.pathname === '/model' ? 'active' : ''}
          >
            Model
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Inference />} />
            <Route path="/model" element={<Model />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
