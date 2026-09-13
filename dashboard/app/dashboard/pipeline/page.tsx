import { listCandidates } from '@/lib/s3'
import { ScoreBadge } from '@/components/Badges'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

const STAGES = [
  { key: 'screened',  label: 'Screened',  color: '#aeaeb2' },
  { key: 'advance',   label: 'Advancing', color: '#0071e3' },
  { key: 'interview', label: 'Interview', color: '#ff9f0a' },
  { key: 'offer',     label: 'Offer',     color: '#af52de' },
  { key: 'hired',     label: 'Hired',     color: '#34c759' },
]

export default async function PipelinePage() {
  const candidates = await listCandidates()

  function getStage(c: any): string {
    const status = c.status?.toLowerCase() ?? ''
    const rec    = c.recommendation?.toLowerCase() ?? ''
    if (status === 'hired')     return 'hired'
    if (status === 'offer')     return 'offer'
    if (status === 'interview') return 'interview'
    if (rec    === 'advance')   return 'advance'
    return 'screened'
  }

  const columns = STAGES.map(s => ({
    ...s,
    candidates: candidates.filter((c: any) => getStage(c) === s.key),
  }))

  return (
    <div className="p-6">
      <div className="mb-5">
        <p className="text-base font-semibold" style={{ color: '#1d1d1f' }}>Pipeline</p>
        <p className="text-xs mt-0.5" style={{ color: '#aeaeb2' }}>Candidate journey across hiring stages</p>
      </div>

      <div className="flex gap-3 overflow-x-auto pb-2">
        {columns.map(col => (
          <div key={col.key} className="shrink-0 w-60">
            {/* Header */}
            <div className="flex items-center justify-between px-1 mb-2">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full" style={{ background: col.color }} />
                <span className="text-xs font-medium" style={{ color: '#1d1d1f' }}>{col.label}</span>
              </div>
              <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                    style={{ background: '#f5f5f7', color: '#6e6e73' }}>
                {col.candidates.length}
              </span>
            </div>

            {/* Cards */}
            <div className="space-y-2 min-h-24">
              {col.candidates.length === 0 ? (
                <div className="rounded-xl py-8 text-center"
                     style={{ border: '1.5px dashed #d2d2d7' }}>
                  <p className="text-xs" style={{ color: '#aeaeb2' }}>Empty</p>
                </div>
              ) : (
                col.candidates.map((c: any, i) => (
                  <Link key={i}
                        href={`/dashboard/candidates/${c.job_id}/${c.candidate_id ?? i}`}
                        className="card block p-3.5 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold"
                           style={{ background: '#f5f5f7', color: '#6e6e73' }}>
                        {c.candidate_name?.[0]?.toUpperCase() ?? 'C'}
                      </div>
                      <ScoreBadge score={c.score} />
                    </div>
                    <p className="text-sm font-medium truncate" style={{ color: '#1d1d1f' }}>
                      {c.candidate_name ?? 'Unknown'}
                    </p>
                    <p className="text-xs mt-0.5 truncate" style={{ color: '#aeaeb2' }}>{c.role ?? '—'}</p>
                  </Link>
                ))
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
