import { Link } from 'react-router-dom';
import { Compiler } from '../types/compiler';
import StatusBadge from './StatusBadge';

interface CompilerCardProps {
  compiler: Compiler;
  onDelete: (id: string) => void;
  onRebuild: (id: string) => void;
}

export default function CompilerCard({ compiler, onDelete, onRebuild }: CompilerCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">{compiler.name}</h3>
          <p className="text-sm text-gray-400">{compiler.id}</p>
        </div>
        <StatusBadge status={compiler.build_status} />
      </div>

      {compiler.build_error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-md">
          <p className="text-xs text-red-400 font-mono">{compiler.build_error}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-400">Memory:</span>
          <span className="ml-2 text-white">{compiler.memory_limit}</span>
        </div>
        <div>
          <span className="text-gray-400">CPU:</span>
          <span className="ml-2 text-white">{compiler.cpu_limit}</span>
        </div>
        <div>
          <span className="text-gray-400">Timeout:</span>
          <span className="ml-2 text-white">{compiler.timeout_seconds}s</span>
        </div>
        <div>
          <span className="text-gray-400">Status:</span>
          <span className="ml-2 text-white">{compiler.enabled ? 'Enabled' : 'Disabled'}</span>
        </div>
      </div>

      {compiler.version && (
        <div className="mb-4">
          <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
            v{compiler.version}
          </span>
        </div>
      )}

      <div className="flex space-x-2 pt-4 border-t border-gray-700">
        <Link
          to={`/compilers/${compiler.id}/edit`}
          className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium text-center transition-colors"
        >
          Edit
        </Link>
        <button
          onClick={() => onRebuild(compiler.id)}
          disabled={compiler.build_status === 'building'}
          className="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Rebuild
        </button>
        <button
          onClick={() => onDelete(compiler.id)}
          className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
