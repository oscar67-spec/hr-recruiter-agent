import { LucideIcon } from 'lucide-react'

export default function StatsCard({
  label, value, icon: Icon,
}: {
  label: string; value: string | number; icon: LucideIcon; color?: string; sub?: string
}) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium" style={{ color: '#6e6e73' }}>{label}</p>
        <div className="w-7 h-7 rounded-lg flex items-center justify-center"
             style={{ background: '#f5f5f7' }}>
          <Icon style={{ width: 14, height: 14, color: '#6e6e73' }} />
        </div>
      </div>
      <p className="text-2xl font-semibold tracking-tight" style={{ color: '#1d1d1f' }}>
        {value}
      </p>
    </div>
  )
}
