import { useState, useEffect } from 'react';
import { compilerApi } from '../api/compilerApi';
import { Compiler } from '../types/compiler';
import CompilerCard from '../components/CompilerCard';
import LoadingSpinner from '../components/LoadingSpinner';
import DeleteConfirmDialog from '../components/DeleteConfirmDialog';
import BuildDrawer from '../components/BuildDrawer';

export default function CompilersListPage() {
  const [compilers, setCompilers] = useState<Compiler[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [compilerToDelete, setCompilerToDelete] = useState<Compiler | null>(null);
  const [buildDrawerOpen, setBuildDrawerOpen] = useState(false);
  const [selectedCompilerId, setSelectedCompilerId] = useState('');
  const [selectedCompilerName, setSelectedCompilerName] = useState('');

  const fetchCompilers = async () => {
    try {
      const data = await compilerApi.listCompilers();
      setCompilers(data);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load compilers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompilers();

    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchCompilers, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleDeleteClick = (compiler: Compiler) => {
    setCompilerToDelete(compiler);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!compilerToDelete) return;

    try {
      await compilerApi.deleteCompiler(compilerToDelete.id);
      setCompilers(compilers.filter((c) => c.id !== compilerToDelete.id));
      setDeleteDialogOpen(false);
      setCompilerToDelete(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to delete compiler');
      setDeleteDialogOpen(false);
    }
  };

  const handleRebuild = async (id: string) => {
    try {
      await compilerApi.rebuildCompiler(id);
      // Refresh list to show updated status
      fetchCompilers();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to trigger rebuild');
    }
  };

  const handleViewBuild = (id: string, name: string) => {
    setSelectedCompilerId(id);
    setSelectedCompilerName(name);
    setBuildDrawerOpen(true);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Compiler Images</h1>
          <p className="text-gray-400 mt-1">
            Manage your runtime environments and execution containers
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-400">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Auto-refreshing every 5s</span>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {compilers.length === 0 ? (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-800 mb-4">
            <svg
              className="w-8 h-8 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No compilers yet</h3>
          <p className="text-gray-400">Get started by creating your first compiler image.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {compilers.map((compiler) => (
            <CompilerCard
              key={compiler.id}
              compiler={compiler}
              onDelete={() => handleDeleteClick(compiler)}
              onRebuild={handleRebuild}
              onViewBuild={handleViewBuild}
            />
          ))}
        </div>
      )}

      <DeleteConfirmDialog
        isOpen={deleteDialogOpen}
        compilerName={compilerToDelete?.name || ''}
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setDeleteDialogOpen(false);
          setCompilerToDelete(null);
        }}
      />

      <BuildDrawer
        isOpen={buildDrawerOpen}
        onClose={() => setBuildDrawerOpen(false)}
        compilerId={selectedCompilerId}
        compilerName={selectedCompilerName}
      />
    </div>
  );
}
