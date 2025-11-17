import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import CompilersListPage from './pages/CompilersListPage';
import CreateCompilerPage from './pages/CreateCompilerPage';
import EditCompilerPage from './pages/EditCompilerPage';
import TemplatesPage from './pages/TemplatesPage';
import TestEnvironmentPage from './pages/TestEnvironmentPage';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-900">
        <Navbar />
        <Routes>
          <Route path="/" element={<CompilersListPage />} />
          <Route path="/compilers/new" element={<CreateCompilerPage />} />
          <Route path="/compilers/:id/edit" element={<EditCompilerPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/test" element={<TestEnvironmentPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
