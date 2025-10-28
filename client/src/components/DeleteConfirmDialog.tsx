interface DeleteConfirmDialogProps {
  isOpen: boolean;
  compilerName: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function DeleteConfirmDialog({
  isOpen,
  compilerName,
  onConfirm,
  onCancel,
}: DeleteConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg max-w-md w-full p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-2">Delete Compiler</h3>
        <p className="text-gray-400 mb-6">
          Are you sure you want to delete <span className="text-white font-semibold">{compilerName}</span>?
          This action cannot be undone and will remove the Docker image.
        </p>
        <div className="flex space-x-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-md bg-gray-700 hover:bg-gray-600 text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded-md bg-red-600 hover:bg-red-700 text-white transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
