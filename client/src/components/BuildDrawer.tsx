import React, { useEffect, useRef, useState } from 'react';
import { compilerApi } from '../api/compilerApi';

interface BuildDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  compilerId: string;
  compilerName: string;
}

interface BuildLog {
  timestamp: string;
  message: string;
  type: 'info' | 'error' | 'success' | 'warning';
}

const BuildDrawer: React.FC<BuildDrawerProps> = ({ isOpen, onClose, compilerId, compilerName }) => {
  const [logs, setLogs] = useState<BuildLog[]>([]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildStatus, setBuildStatus] = useState<'idle' | 'building' | 'success' | 'failed'>('idle');
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Add log helper
  const addLog = (message: string, type: BuildLog['type'] = 'info') => {
    const newLog: BuildLog = {
      timestamp: new Date().toLocaleTimeString(),
      message,
      type,
    };
    setLogs((prev) => [...prev, newLog]);
  };

  // Start build process or monitoring
  const startBuild = async () => {
    setIsBuilding(true);
    setBuildStatus('building');

    addLog(`Starting build for ${compilerName}...`, 'info');
    addLog(`Compiler ID: ${compilerId}`, 'info');
    addLog('Sending build request to server...', 'info');

    try {
      // Trigger the build via API
      await compilerApi.rebuildCompiler(compilerId);
      addLog('Build request accepted by server', 'success');
      addLog('Docker image build queued', 'info');
      addLog('Waiting for builder to process...', 'info');

      // Start polling for status and logs
      pollBuildStatus();
    } catch (error: any) {
      addLog(`Failed to start build: ${error.message}`, 'error');
      setBuildStatus('failed');
      setIsBuilding(false);
    }
  };

  // Poll compiler status and logs to track build progress
  const pollBuildStatus = async () => {
    let previousLogs = '';

    const pollInterval = setInterval(async () => {
      try {
        const logsData = await compilerApi.getBuildLogs(compilerId);

        // Check if logs have been updated
        if (logsData.build_logs && logsData.build_logs !== previousLogs) {
          // New logs available - display only new lines
          if (previousLogs === '') {
            // First fetch - show all logs
            addLog('--- Build Output ---', 'info');
            const logLines = logsData.build_logs.split('\n');
            logLines.forEach((line) => {
              if (line.trim()) {
                let logType: BuildLog['type'] = 'info';
                if (line.includes('ERROR') || line.includes('STDERR')) {
                  logType = 'error';
                } else if (line.includes('Successfully')) {
                  logType = 'success';
                }
                addLog(line, logType);
              }
            });
          } else {
            // Incremental update - show only new lines
            const newContent = logsData.build_logs.substring(previousLogs.length);
            const newLines = newContent.split('\n');
            newLines.forEach((line) => {
              if (line.trim()) {
                let logType: BuildLog['type'] = 'info';
                if (line.includes('ERROR') || line.includes('STDERR')) {
                  logType = 'error';
                } else if (line.includes('Successfully')) {
                  logType = 'success';
                }
                addLog(line, logType);
              }
            });
          }
          previousLogs = logsData.build_logs;
        }

        // Check build status
        if (logsData.build_status === 'building') {
          // Still building - continue polling
        } else if (logsData.build_status === 'ready') {
          addLog('Docker image built successfully!', 'success');
          if (logsData.built_at) {
            addLog(`Completed at: ${new Date(logsData.built_at).toLocaleString()}`, 'info');
          }
          setBuildStatus('success');
          setIsBuilding(false);
          clearInterval(pollInterval);
        } else if (logsData.build_status === 'failed') {
          addLog('Build failed!', 'error');
          if (logsData.build_error) {
            addLog(`Error: ${logsData.build_error}`, 'error');
          }
          setBuildStatus('failed');
          setIsBuilding(false);
          clearInterval(pollInterval);
        }
      } catch (error: any) {
        addLog(`Status check failed: ${error.message}`, 'error');
        clearInterval(pollInterval);
        setIsBuilding(false);
      }
    }, 2000); // Poll every 2 seconds

    // Safety timeout after 15 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (isBuilding) {
        addLog('Build monitoring timeout - refresh the drawer to see final status', 'warning');
        setIsBuilding(false);
      }
    }, 900000);
  };

  // Load current build status when drawer opens
  useEffect(() => {
    if (isOpen && compilerId) {
      loadCurrentStatus();
    } else if (!isOpen) {
      // Reset after animation completes
      setTimeout(() => {
        setLogs([]);
        setBuildStatus('idle');
      }, 300);
    }
  }, [isOpen, compilerId]);

  // Load current compiler status and build logs
  const loadCurrentStatus = async () => {
    try {
      const logsData = await compilerApi.getBuildLogs(compilerId);

      addLog('Fetching current build status...', 'info');
      addLog(`Current status: ${logsData.build_status}`, 'info');

      // Display existing build logs if available
      if (logsData.build_logs && logsData.build_logs !== 'No build logs available') {
        addLog('--- Previous Build Logs ---', 'info');
        // Parse and display the logs
        const logLines = logsData.build_logs.split('\n');
        logLines.forEach((line) => {
          if (line.trim()) {
            // Determine log type based on content
            let logType: BuildLog['type'] = 'info';
            if (line.includes('ERROR') || line.includes('STDERR') || line.includes('failed')) {
              logType = 'error';
            } else if (line.includes('SUCCESS') || line.includes('Successfully')) {
              logType = 'success';
            } else if (line.includes('WARNING') || line.includes('pending')) {
              logType = 'warning';
            }
            addLog(line, logType);
          }
        });
        addLog('--- End of Previous Build Logs ---', 'info');
      }

      if (logsData.build_status === 'ready') {
        addLog('Compiler is ready', 'success');
        if (logsData.built_at) {
          addLog(`Last built: ${new Date(logsData.built_at).toLocaleString()}`, 'info');
        }
        setBuildStatus('success');
      } else if (logsData.build_status === 'building') {
        addLog('Build currently in progress', 'warning');
        addLog('Click "Start Monitoring" to track live progress', 'info');
        setBuildStatus('building');
      } else if (logsData.build_status === 'failed') {
        addLog('Last build failed', 'error');
        if (logsData.build_error) {
          addLog(`Error: ${logsData.build_error}`, 'error');
        }
        setBuildStatus('failed');
      } else if (logsData.build_status === 'pending') {
        addLog('Build is pending', 'warning');
        addLog('Waiting in build queue', 'info');
      }
    } catch (error: any) {
      addLog(`Failed to fetch status: ${error.message}`, 'error');
    }
  };

  const getLogColor = (type: BuildLog['type']) => {
    switch (type) {
      case 'error':
        return 'text-red-400';
      case 'success':
        return 'text-green-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-gray-300';
    }
  };

  const getStatusBadge = () => {
    switch (buildStatus) {
      case 'building':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-blue-900/50 text-blue-300">
            <svg className="animate-spin -ml-0.5 mr-1.5 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Building
          </span>
        );
      case 'success':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-green-900/50 text-green-300">
            ✓ Success
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-red-900/50 text-red-300">
            ✗ Failed
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity z-40"
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed top-0 right-0 h-full w-full md:w-2/3 lg:w-1/2 bg-gray-900 shadow-xl transform transition-transform duration-300 ease-in-out z-50 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold text-white">Build Output</h2>
            {getStatusBadge()}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-1"
            aria-label="Close drawer"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Compiler Info */}
        <div className="p-4 bg-gray-800/50 border-b border-gray-700">
          <div className="text-sm">
            <span className="text-gray-400">Compiler:</span>{' '}
            <span className="text-white font-medium">{compilerName}</span>
          </div>
          <div className="text-sm mt-1">
            <span className="text-gray-400">ID:</span>{' '}
            <span className="text-gray-300 font-mono text-xs">{compilerId}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="p-4 border-b border-gray-700">
          <button
            onClick={startBuild}
            disabled={isBuilding}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isBuilding
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isBuilding ? 'Monitoring...' : buildStatus === 'building' ? 'Start Monitoring' : 'Start New Build'}
          </button>
          {logs.length > 0 && (
            <button
              onClick={() => setLogs([])}
              disabled={isBuilding}
              className="ml-2 px-4 py-2 rounded-lg font-medium bg-gray-700 hover:bg-gray-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear Logs
            </button>
          )}
        </div>

        {/* Logs Container */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-950" style={{ height: 'calc(100vh - 220px)' }}>
          {logs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-lg">No build logs yet</p>
                <p className="text-sm mt-2">Click "Start Build" to begin</p>
              </div>
            </div>
          ) : (
            <div className="font-mono text-sm space-y-1">
              {logs.map((log, index) => (
                <div key={index} className="flex gap-3">
                  <span className="text-gray-500 select-none">{log.timestamp}</span>
                  <span className={getLogColor(log.type)}>{log.message}</span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default BuildDrawer;
