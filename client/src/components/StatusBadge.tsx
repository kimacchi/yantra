import { BuildStatus } from '../types/compiler';

interface StatusBadgeProps {
  status: BuildStatus;
}

const statusConfig: Record<BuildStatus, { label: string; className: string }> = {
  pending: {
    label: 'Pending',
    className: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  },
  building: {
    label: 'Building',
    className: 'bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse',
  },
  ready: {
    label: 'Ready',
    className: 'bg-green-500/20 text-green-400 border-green-500/30',
  },
  failed: {
    label: 'Failed',
    className: 'bg-red-500/20 text-red-400 border-red-500/30',
  },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${config.className}`}
    >
      <span className="w-2 h-2 rounded-full mr-2 bg-current" />
      {config.label}
    </span>
  );
}
