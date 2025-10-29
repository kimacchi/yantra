import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { templateApi } from '../api/templateApi';
import { DockerfileTemplate } from '../types/template';
import LoadingSpinner from '../components/LoadingSpinner';

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<DockerfileTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [officialOnly, setOfficialOnly] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<DockerfileTemplate | null>(null);
  const navigate = useNavigate();

  const fetchTemplates = async () => {
    try {
      const data = await templateApi.listTemplates(selectedCategory || undefined, officialOnly);
      setTemplates(data);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchTemplates();
  }, [selectedCategory, officialOnly]);

  const categories = ['language', 'framework', 'tool', 'os'];

  const handleUseTemplate = (template: DockerfileTemplate) => {
    // Navigate to create compiler page with template pre-filled
    navigate('/compilers/new', {
      state: {
        template: {
          dockerfile_content: template.dockerfile_template,
          run_command: template.default_run_command || [],
          suggestedId: template.id,
          suggestedName: template.name
        }
      }
    });
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dockerfile Templates</h1>
        <p className="text-gray-400 mt-1">
          Browse and use pre-built Dockerfile templates for your compiler images
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value="">All</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="official-only"
            checked={officialOnly}
            onChange={(e) => setOfficialOnly(e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
          />
          <label htmlFor="official-only" className="text-sm text-gray-400">
            Official templates only
          </label>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {templates.length === 0 ? (
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No templates found</h3>
          <p className="text-gray-400">Try adjusting your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div
              key={template.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-colors cursor-pointer"
              onClick={() => setSelectedTemplate(template)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  {template.icon && <span className="text-2xl">{template.icon}</span>}
                  <h3 className="text-xl font-semibold text-white">{template.name}</h3>
                </div>
                {template.is_official && (
                  <span className="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-400 rounded">
                    Official
                  </span>
                )}
              </div>
              <p className="text-gray-400 text-sm mb-4">{template.description}</p>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-2 py-1 text-xs font-medium bg-gray-700 text-gray-300 rounded">
                  {template.category}
                </span>
                {template.tags?.map((tag) => (
                  <span key={tag} className="px-2 py-1 text-xs font-medium bg-gray-700 text-gray-300 rounded">
                    {tag}
                  </span>
                ))}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleUseTemplate(template);
                }}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Use Template
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Template Details Modal */}
      {selectedTemplate && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedTemplate(null)}
        >
          <div
            className="bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {selectedTemplate.icon && <span className="text-3xl">{selectedTemplate.icon}</span>}
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedTemplate.name}</h2>
                    <p className="text-gray-400 text-sm">by {selectedTemplate.author}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTemplate(null)}
                  className="text-gray-400 hover:text-white"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
              <p className="text-gray-300 mb-6">{selectedTemplate.description}</p>
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-2">Dockerfile</h3>
                <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto">
                  <code className="text-sm text-gray-300">{selectedTemplate.dockerfile_template}</code>
                </pre>
              </div>
              {selectedTemplate.default_run_command && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-white mb-2">Default Run Command</h3>
                  <pre className="bg-gray-900 p-4 rounded-lg">
                    <code className="text-sm text-gray-300">
                      {JSON.stringify(selectedTemplate.default_run_command, null, 2)}
                    </code>
                  </pre>
                </div>
              )}
              <button
                onClick={() => handleUseTemplate(selectedTemplate)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
              >
                Use This Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
