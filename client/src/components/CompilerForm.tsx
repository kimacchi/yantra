import { useState } from 'react';
import CodeEditor from './CodeEditor';
import { CreateCompilerRequest, UpdateCompilerRequest } from '../types/compiler';

interface CompilerFormProps {
  initialData?: Partial<CreateCompilerRequest>;
  onSubmit: (data: CreateCompilerRequest | UpdateCompilerRequest) => Promise<void>;
  isEdit?: boolean;
  isLoading?: boolean;
}

export default function CompilerForm({
  initialData = {},
  onSubmit,
  isEdit = false,
  isLoading = false,
}: CompilerFormProps) {
  const [id, setId] = useState(initialData.id || '');
  const [name, setName] = useState(initialData.name || '');
  const [dockerfileContent, setDockerfileContent] = useState(initialData.dockerfile_content || '');
  const [runCommand, setRunCommand] = useState(
    initialData.run_command ? JSON.stringify(initialData.run_command) : '["node", "-"]'
  );
  const [version, setVersion] = useState(initialData.version || '');
  const [memoryLimit, setMemoryLimit] = useState(initialData.memory_limit || '512m');
  const [cpuLimit, setCpuLimit] = useState(initialData.cpu_limit || '1');
  const [timeoutSeconds, setTimeoutSeconds] = useState(initialData.timeout_seconds?.toString() || '10');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      // Parse run command JSON
      let parsedRunCommand: string[];
      try {
        parsedRunCommand = JSON.parse(runCommand);
        if (!Array.isArray(parsedRunCommand)) {
          throw new Error('Run command must be an array');
        }
      } catch {
        setError('Invalid run command format. Must be a JSON array like ["node", "-"]');
        return;
      }

      // JSON encoding will handle newlines automatically
      const data: CreateCompilerRequest | UpdateCompilerRequest = isEdit
        ? {
            name,
            dockerfile_content: dockerfileContent,
            run_command: parsedRunCommand,
            version: version || undefined,
            memory_limit: memoryLimit,
            cpu_limit: cpuLimit,
            timeout_seconds: parseInt(timeoutSeconds),
          }
        : {
            id,
            name,
            dockerfile_content: dockerfileContent,
            run_command: parsedRunCommand,
            version: version || undefined,
            memory_limit: memoryLimit,
            cpu_limit: cpuLimit,
            timeout_seconds: parseInt(timeoutSeconds),
          };

      await onSubmit(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Compiler ID {!isEdit && <span className="text-red-400">*</span>}
          </label>
          <input
            type="text"
            value={id}
            onChange={(e) => setId(e.target.value)}
            disabled={isEdit}
            required={!isEdit}
            placeholder="e.g., python-3.11, node-20"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Name <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="e.g., Python 3.11, Node.js 20"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Version</label>
          <input
            type="text"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            placeholder="e.g., 1.0.0"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Memory Limit <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={memoryLimit}
            onChange={(e) => setMemoryLimit(e.target.value)}
            required
            placeholder="e.g., 512m, 1g"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            CPU Limit <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={cpuLimit}
            onChange={(e) => setCpuLimit(e.target.value)}
            required
            placeholder="e.g., 0.5, 1, 2"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Timeout (seconds) <span className="text-red-400">*</span>
          </label>
          <input
            type="number"
            value={timeoutSeconds}
            onChange={(e) => setTimeoutSeconds(e.target.value)}
            required
            placeholder="10"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Run Command (JSON array) <span className="text-red-400">*</span>
        </label>
        <input
          type="text"
          value={runCommand}
          onChange={(e) => setRunCommand(e.target.value)}
          required
          placeholder='["python", "-"] or ["node", "-"]'
          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
        />
        <p className="mt-1 text-xs text-gray-400">
          Must be a valid JSON array, e.g., ["node", "-"] or ["python", "-"]
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Dockerfile <span className="text-red-400">*</span>
        </label>
        <CodeEditor value={dockerfileContent} onChange={setDockerfileContent} height="400px" />
        <p className="mt-2 text-xs text-gray-400">
          Write your Dockerfile here. Use proper Dockerfile syntax with actual newlines.
        </p>
      </div>

      <div className="flex space-x-4">
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : isEdit ? 'Update Compiler' : 'Create Compiler'}
        </button>
      </div>
    </form>
  );
}
