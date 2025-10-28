import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import CompilersListPage from './pages/CompilersListPage';
import CreateCompilerPage from './pages/CreateCompilerPage';
import EditCompilerPage from './pages/EditCompilerPage';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-900">
        <Navbar />
        <Routes>
          <Route path="/" element={<CompilersListPage />} />
          <Route path="/compilers/new" element={<CreateCompilerPage />} />
          <Route path="/compilers/:id/edit" element={<EditCompilerPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
