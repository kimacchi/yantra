import { useState, useEffect } from 'react';
import { compilerApi } from '../api/compilerApi';
import { submissionApi } from '../api/submissionApi';
import { Compiler } from '../types/compiler';
import { ExecutionResult } from '../types/submission';
import LoadingSpinner from '../components/LoadingSpinner';

export default function TestEnvironmentPage() {
  const [compilers, setCompilers] = useState<Compiler[]>([]);
  const [selectedCompiler, setSelectedCompiler] = useState<string>('');
  const [code, setCode] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [error, setError] = useState('');

  // Fetch ready compilers
  useEffect(() => {
    const fetchCompilers = async () => {
      try {
        const data = await compilerApi.listCompilers(true); // Only enabled compilers
        const readyCompilers = data.filter(c => c.build_status === 'ready');
        setCompilers(readyCompilers);

        // Auto-select first compiler
        if (readyCompilers.length > 0) {
          setSelectedCompiler(readyCompilers[0].id);
          // Set default code based on language
          setCode(getDefaultCode(readyCompilers[0].id));
        }

        setError('');
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load compilers');
      } finally {
        setLoading(false);
      }
    };

    fetchCompilers();
  }, []);

  // Get default code for a language
  const getDefaultCode = (compilerId: string): string => {
    const defaults: Record<string, string> = {
      python: 'print("Hello, World!")',
      node: 'console.log("Hello, World!");',
      java: `public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}`,
      cpp: `#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}`,
      c: `#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}`,
      rust: `fn main() {
    println!("Hello, World!");
}`,
      go: `package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}`,
    };

    // Try to match by compiler ID
    for (const [key, value] of Object.entries(defaults)) {
      if (compilerId.toLowerCase().includes(key)) {
        return value;
      }
    }

    return '// Write your code here';
  };

  // Handle compiler change
  const handleCompilerChange = (compilerId: string) => {
    setSelectedCompiler(compilerId);
    setCode(getDefaultCode(compilerId));
    setResult(null);
    setError('');
  };

  // Poll for results
  const pollResults = async (jobId: string, maxAttempts = 30) => {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const result = await submissionApi.getResults(jobId);

        if (result.status === 'COMPLETED' || result.status === 'FAILED' ||
            result.status === 'TIMEOUT' || result.status === 'ERROR') {
          setResult(result);
          setExecuting(false);
          return;
        }

        // Update status while waiting
        setResult(result);

        // Wait 500ms before next poll
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch results');
        setExecuting(false);
        return;
      }
    }

    // Timeout after 15 seconds of polling
    setError('Polling timeout: Results took too long to fetch');
    setExecuting(false);
  };

  // Execute code
  const handleExecute = async () => {
    if (!selectedCompiler) {
      setError('Please select a compiler');
      return;
    }

    if (!code.trim()) {
      setError('Please enter some code');
      return;
    }

    setExecuting(true);
    setResult(null);
    setError('');

    try {
      const response = await submissionApi.submitCode({
        code,
        language: selectedCompiler,
      });

      // Start polling for results
      await pollResults(response.job_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to submit code');
      setExecuting(false);
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'FAILED':
      case 'ERROR':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'TIMEOUT':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'RUNNING':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse';
      case 'PENDING':
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
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
        <h1 className="text-3xl font-bold text-white">Test Environment</h1>
        <p className="text-gray-400 mt-1">
          Write and execute code using your active compilers
        </p>
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
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No ready compilers</h3>
          <p className="text-gray-400">
            Create and build a compiler first to start testing code.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Code Editor */}
          <div className="space-y-4">
            {/* Compiler Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select Compiler
              </label>
              <select
                value={selectedCompiler}
                onChange={(e) => handleCompilerChange(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {compilers.map((compiler) => (
                  <option key={compiler.id} value={compiler.id}>
                    {compiler.name} {compiler.version && `(${compiler.version})`}
                  </option>
                ))}
              </select>
            </div>

            {/* Code Editor */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Code
              </label>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-96 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Write your code here..."
                spellCheck={false}
              />
            </div>

            {/* Execute Button */}
            <button
              onClick={handleExecute}
              disabled={executing || !selectedCompiler}
              className={`w-full px-6 py-3 rounded-lg font-medium transition-colors ${
                executing || !selectedCompiler
                  ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {executing ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Executing...
                </span>
              ) : (
                'Run Code'
              )}
            </button>
          </div>

          {/* Right Panel - Output */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Output
              </label>

              {result ? (
                <div className="space-y-4">
                  {/* Status Badge */}
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(result.status)}`}>
                    {result.status}
                  </div>

                  {/* Stdout */}
                  {result.stdout && (
                    <div>
                      <div className="text-xs font-medium text-gray-400 mb-2">STDOUT</div>
                      <pre className="p-4 bg-gray-800 border border-gray-700 rounded-lg text-green-400 text-sm font-mono overflow-x-auto whitespace-pre-wrap break-words">
                        {result.stdout}
                      </pre>
                    </div>
                  )}

                  {/* Stderr */}
                  {result.stderr && (
                    <div>
                      <div className="text-xs font-medium text-gray-400 mb-2">STDERR</div>
                      <pre className="p-4 bg-gray-800 border border-red-500/30 rounded-lg text-red-400 text-sm font-mono overflow-x-auto whitespace-pre-wrap break-words">
                        {result.stderr}
                      </pre>
                    </div>
                  )}

                  {/* Empty output message */}
                  {!result.stdout && !result.stderr && result.status === 'COMPLETED' && (
                    <div className="p-4 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 text-sm">
                      No output
                    </div>
                  )}

                  {/* Completed timestamp */}
                  {result.completed_at && (
                    <div className="text-xs text-gray-500">
                      Completed at: {new Date(result.completed_at).toLocaleString()}
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-96 flex items-center justify-center bg-gray-800 border border-gray-700 rounded-lg">
                  <div className="text-center text-gray-500">
                    <svg
                      className="w-12 h-12 mx-auto mb-3 opacity-50"
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
                    <p>Run your code to see the output here</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
