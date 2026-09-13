import { listJobs, listCandidates } from '@/lib/s3'
import StatsCard from '@/components/StatsCard'
import RecentCandidates from '@/components/RecentCandidates'
import { Briefcase, Users, TrendingUp, CheckCircle } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const [jobs, candidates] = await Promise.all([listJobs(), listCandidates()])

  const openJobs  = jobs.filter((j: any) => j.status === 'open').length
  const total     = candidates.length
  const avgScore  = total ? Math.round(candidates.reduce((s: number, c: any) => s + (c.score ?? 0), 0) / total) : 0
  const advancing = candidates.filter((c: any) => c.recommendation?.toLowerCase() === 'advance').length

  return (
    <div className="p-6 space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatsCard label="Open Roles"       value={openJobs}          icon={Briefcase}   />
        <StatsCard label="Total Candidates" value={total}             icon={Users}       />
        <StatsCard label="Avg AI Score"     value={`${avgScore}/100`} icon={TrendingUp}  />
        <StatsCard label="Ready to Advance" value={advancing}         icon={CheckCircle} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <div className="card lg:col-span-2 p-5">
          <p className="text-sm font-medium mb-0.5" style={{ color: '#1d1d1f' }}>Score Distribution</p>
          <p className="text-xs mb-5" style={{ color: '#aeaeb2' }}>AI screening results across all candidates</p>
          <ScoreBars candidates={candidates} />
        </div>
        <div className="card p-5">
          <p className="text-sm font-medium mb-0.5" style={{ color: '#1d1d1f' }}>Recommendations</p>
          <p className="text-xs mb-5" style={{ color: '#aeaeb2' }}>Pipeline breakdown</p>
          <RecBreakdown candidates={candidates} />
        </div>
      </div>

      {/* Table */}
      <div className="card p-5">
        <p className="text-sm font-medium mb-0.5" style={{ color: '#1d1d1f' }}>Recent Candidates</p>
        <p className="text-xs mb-5" style={{ color: '#aeaeb2' }}>Sorted by AI score</p>
        <RecentCandidates candidates={candidates.slice(0, 8)} />
      </div>
    </div>
  )
}

function ScoreBars({ candidates }: { candidates: any[] }) {
  const buckets = [
    { label: '90–100', min: 90,  color: '#34c759' },
    { label: '75–89',  min: 75,  color: '#0071e3' },
    { label: '60–74',  min: 60,  color: '#ff9f0a' },
    { label: '< 60',   min: 0,   color: '#ff3b30' },
  ]
  const max = candidates.length || 1
  return (
    <div className="space-y-3.5">
      {buckets.map((b, i) => {
        const next  = buckets[i + 1]?.min ?? 101
        const count = candidates.filter((c: any) => c.score >= b.min && c.score < next).length
        return (
          <div key={b.label} className="flex items-center gap-3">
            <span className="text-xs w-14 shrink-0" style={{ color: '#6e6e73' }}>{b.label}</span>
            <div className="flex-1 rounded-full h-1.5 overflow-hidden" style={{ background: '#f5f5f7' }}>
              <div className="h-1.5 rounded-full transition-all duration-700"
                   style={{ width: `${Math.max((count / max) * 100, count > 0 ? 3 : 0)}%`, background: b.color }} />
            </div>
            <span className="text-xs font-medium w-4 text-right" style={{ color: '#1d1d1f' }}>{count}</span>
          </div>
        )
      })}
    </div>
  )
}

function RecBreakdown({ candidates }: { candidates: any[] }) {
  const total   = candidates.length || 1
  const advance = candidates.filter((c: any) => c.recommendation?.toLowerCase() === 'advance').length
  const hold    = candidates.filter((c: any) => c.recommendation?.toLowerCase() === 'hold').length
  const reject  = candidates.filter((c: any) => c.recommendation?.toLowerCase() === 'reject').length

  return (
    <div className="space-y-4">
      {[
        { label: 'Advance', count: advance, color: '#34c759' },
        { label: 'Hold',    count: hold,    color: '#ff9f0a' },
        { label: 'Reject',  count: reject,  color: '#ff3b30' },
      ].map(item => (
        <div key={item.label}>
          <div className="flex justify-between mb-1.5">
            <span className="text-xs font-medium" style={{ color: '#1d1d1f' }}>{item.label}</span>
            <span className="text-xs" style={{ color: '#aeaeb2' }}>{item.count} / {candidates.length}</span>
          </div>
          <div className="rounded-full h-1.5" style={{ background: '#f5f5f7' }}>
            <div className="h-1.5 rounded-full transition-all duration-700"
                 style={{ width: `${Math.max((item.count / total) * 100, item.count > 0 ? 3 : 0)}%`, background: item.color }} />
          </div>
        </div>
      ))}
      <p className="text-xs text-center pt-1" style={{ color: '#aeaeb2' }}>{candidates.length} total</p>
    </div>
  )
}
