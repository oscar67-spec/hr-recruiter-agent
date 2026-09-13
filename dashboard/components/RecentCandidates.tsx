import Link from 'next/link'
import { ScoreBadge, RecBadge } from './Badges'

export default function RecentCandidates({ candidates }: { candidates: any[] }) {
  if (!candidates.length) {
    return <p className="text-sm text-center py-10" style={{ color: '#aeaeb2' }}>No candidates yet.</p>
  }
  return (
    <table className="w-full">
      <thead>
        <tr style={{ borderBottom: '1px solid #f5f5f7' }}>
          {['Name', 'Role', 'Score', 'Recommendation', 'Status'].map(h => (
            <th key={h} className="text-left pb-3 pr-6 last:pr-0 text-xs font-medium"
                style={{ color: '#aeaeb2' }}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {candidates.map((c: any, i) => (
          <tr key={i} className="group" style={{ borderBottom: '1px solid #f5f5f7' }}>
            <td className="py-3.5 pr-6">
              <Link href={`/dashboard/candidates/${c.job_id}/${c.candidate_id ?? i}`}
                    className="text-sm font-medium hover:underline"
                    style={{ color: '#1d1d1f' }}>
                {c.candidate_name ?? 'Unknown'}
              </Link>
              <p className="text-xs mt-0.5" style={{ color: '#aeaeb2' }}>{c.candidate_email}</p>
            </td>
            <td className="py-3.5 pr-6 text-sm" style={{ color: '#6e6e73' }}>{c.role ?? '—'}</td>
            <td className="py-3.5 pr-6"><ScoreBadge score={c.score} /></td>
            <td className="py-3.5 pr-6"><RecBadge rec={c.recommendation} /></td>
            <td className="py-3.5">
              <span className="text-xs font-medium px-2.5 py-1 rounded-full capitalize"
                    style={{ background: '#f5f5f7', color: '#6e6e73' }}>
                {c.status ?? 'screened'}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
