import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { compilerApi } from '../api/compilerApi';
import { CreateCompilerRequest } from '../types/compiler';
import CompilerForm from '../components/CompilerForm';

export default function CreateCompilerPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(false);

  // Get template data from navigation state if available
  const templateData = location.state?.template;

  const handleSubmit = async (data: CreateCompilerRequest) => {
    setIsLoading(true);
    try {
      await compilerApi.createCompiler(data);
      navigate('/');
    } catch (error) {
      setIsLoading(false);
      throw error; // Let CompilerForm handle the error display
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <button
          onClick={() => navigate('/')}
          className="text-gray-400 hover:text-white mb-4 flex items-center space-x-2 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span>Back to compilers</span>
        </button>
        <h1 className="text-3xl font-bold text-white">Create New Compiler</h1>
        <p className="text-gray-400 mt-1">
          {templateData ? 'Using template to create runtime environment' : 'Define a new runtime environment for code execution'}
        </p>
      </div>

      {templateData && (
        <div className="mb-4 bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
          <p className="text-blue-400">
            Template loaded: <span className="font-semibold">{templateData.suggestedName}</span>
          </p>
        </div>
      )}

      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <CompilerForm onSubmit={handleSubmit} isLoading={isLoading} initialData={templateData} />
      </div>
    </div>
  );
}
