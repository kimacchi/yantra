export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="relative">
        <div className="w-12 h-12 rounded-full border-4 border-gray-700 border-t-blue-500 animate-spin"></div>
      </div>
    </div>
  );
}
