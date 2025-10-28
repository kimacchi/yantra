import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { compilerApi } from '../api/compilerApi';
import { Compiler, UpdateCompilerRequest } from '../types/compiler';
import CompilerForm from '../components/CompilerForm';
import LoadingSpinner from '../components/LoadingSpinner';

export default function EditCompilerPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [compiler, setCompiler] = useState<Compiler | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchCompiler = async () => {
      if (!id) return;

      try {
        const data = await compilerApi.getCompiler(id);
        // JSON decoding handles newlines automatically
        setCompiler(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load compiler');
      } finally {
        setLoading(false);
      }
    };

    fetchCompiler();
  }, [id]);

  const handleSubmit = async (data: UpdateCompilerRequest) => {
    if (!id) return;

    setIsSubmitting(true);
    try {
      await compilerApi.updateCompiler(id, data);
      navigate('/');
    } catch (error) {
      setIsSubmitting(false);
      throw error; // Let CompilerForm handle the error display
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !compiler) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-400">{error || 'Compiler not found'}</p>
        </div>
      </div>
    );
  }

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
        <h1 className="text-3xl font-bold text-white">Edit Compiler</h1>
        <p className="text-gray-400 mt-1">
          Update the configuration for <span className="text-white font-semibold">{compiler.name}</span>
        </p>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <CompilerForm
          initialData={{
            id: compiler.id,
            name: compiler.name,
            dockerfile_content: compiler.dockerfile_content,
            run_command: compiler.run_command,
            version: compiler.version || undefined,
            memory_limit: compiler.memory_limit,
            cpu_limit: compiler.cpu_limit,
            timeout_seconds: compiler.timeout_seconds,
          }}
          onSubmit={handleSubmit}
          isEdit
          isLoading={isSubmitting}
        />
      </div>
    </div>
  );
}
