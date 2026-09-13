export function ScoreBadge({ score }: { score?: number }) {
  const s = score ?? 0
  const { bg, color } =
    s >= 80 ? { bg: '#d1fae5', color: '#059669' } :
    s >= 60 ? { bg: '#fff3cd', color: '#d97706' } :
              { bg: '#fee2e2', color: '#dc2626' }
  return (
    <span className="text-xs font-medium px-2.5 py-1 rounded-full"
          style={{ background: bg, color }}>
      {s}/100
    </span>
  )
}

export function RecBadge({ rec }: { rec?: string }) {
  const r = rec?.toLowerCase() ?? ''
  const { bg, color } =
    r === 'advance' ? { bg: '#d1fae5', color: '#059669' } :
    r === 'hold'    ? { bg: '#fff3cd', color: '#d97706' } :
    r === 'reject'  ? { bg: '#fee2e2', color: '#dc2626' } :
                      { bg: '#f5f5f7', color: '#6e6e73' }
  return (
    <span className="text-xs font-medium px-2.5 py-1 rounded-full capitalize"
          style={{ background: bg, color }}>
      {rec ?? 'N/A'}
    </span>
  )
}
