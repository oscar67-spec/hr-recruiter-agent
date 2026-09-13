import { listCandidates, listJobs } from '@/lib/s3'
import Link from 'next/link'
import { ScoreBadge, RecBadge } from '@/components/Badges'
import { Users } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function CandidatesPage({
  searchParams,
}: { searchParams: Promise<{ job_id?: string; rec?: string }> }) {
  const { job_id, rec: recParam } = await searchParams
  const [allCandidates, jobs] = await Promise.all([listCandidates(job_id), listJobs()])
  const rec = recParam?.toLowerCase()
  const candidates = allCandidates.filter((c: any) => !rec || c.recommendation?.toLowerCase() === rec)

  return (
    <div className="p-6">
      <div className="mb-5">
        <p className="text-base font-semibold" style={{ color: '#1d1d1f' }}>Candidates</p>
        <p className="text-xs mt-0.5" style={{ color: '#aeaeb2' }}>
          {candidates.length} candidate{candidates.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Filters */}
      <div className="card px-4 py-3 mb-4 flex flex-wrap gap-2 items-center">
        <span className="text-xs font-medium mr-1" style={{ color: '#6e6e73' }}>Filter</span>
        <Pill href="/dashboard/candidates" label="All" active={!job_id && !rec} />
        {jobs.map((j: any) => (
          <Pill key={j.job_id} href={`/dashboard/candidates?job_id=${j.job_id}`}
                label={j.role ?? j.job_id} active={job_id === j.job_id} />
        ))}
        <div className="w-px h-4" style={{ background: '#d2d2d7' }} />
        {['advance', 'hold', 'reject'].map(r => (
          <Pill key={r}
                href={`/dashboard/candidates?${job_id ? `job_id=${job_id}&` : ''}rec=${r}`}
                label={r[0].toUpperCase() + r.slice(1)} active={rec === r} />
        ))}
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {candidates.length === 0 ? (
          <div className="py-16 text-center">
            <Users className="w-8 h-8 mx-auto mb-3" style={{ color: '#d2d2d7' }} />
            <p className="text-sm" style={{ color: '#6e6e73' }}>No candidates found</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #f5f5f7', background: '#fafafa' }}>
                {['Candidate', 'Role', 'Score', 'Recommendation', 'Strengths', ''].map(h => (
                  <th key={h} className="text-left text-xs font-medium px-5 py-3"
                      style={{ color: '#aeaeb2' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {candidates.map((c: any, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f5f5f7' }}
                    className="hover:bg-[#fafafa] transition-colors">
                  <td className="px-5 py-4">
                    <p className="text-sm font-medium" style={{ color: '#1d1d1f' }}>{c.candidate_name ?? 'Unknown'}</p>
                    <p className="text-xs mt-0.5" style={{ color: '#aeaeb2' }}>{c.candidate_email}</p>
                  </td>
                  <td className="px-5 py-4 text-sm" style={{ color: '#6e6e73' }}>{c.role ?? '—'}</td>
                  <td className="px-5 py-4"><ScoreBadge score={c.score} /></td>
                  <td className="px-5 py-4"><RecBadge rec={c.recommendation} /></td>
                  <td className="px-5 py-4 text-xs max-w-xs truncate" style={{ color: '#6e6e73' }}>{c.strengths ?? '—'}</td>
                  <td className="px-5 py-4">
                    <Link href={`/dashboard/candidates/${c.job_id}/${c.candidate_id ?? i}`}
                          className="text-xs font-medium" style={{ color: '#0071e3' }}>View →</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

function Pill({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <Link href={href} className="text-xs font-medium px-3 py-1.5 rounded-full transition-colors"
          style={active ? { background: '#1d1d1f', color: '#ffffff' } : { background: '#f5f5f7', color: '#6e6e73' }}>
      {label}
    </Link>
  )
}
