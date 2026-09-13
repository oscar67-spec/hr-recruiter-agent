'use client'
import { usePathname } from 'next/navigation'

const labels: Record<string, string> = {
  '/dashboard':            'Overview',
  '/dashboard/jobs':       'Jobs',
  '/dashboard/candidates': 'Candidates',
  '/dashboard/pipeline':   'Pipeline',
}

export default function TopNav() {
  const path = usePathname()
  const label = labels[path] ?? 'Dashboard'

  return (
    <div className="px-6 py-4 flex items-center justify-between"
         style={{ background: '#ffffff', borderBottom: '1px solid #f5f5f7' }}>
      <div>
        <p className="text-xs" style={{ color: '#aeaeb2' }}>Dashboard / {label}</p>
        <h1 className="text-base font-semibold" style={{ color: '#1d1d1f' }}>{label}</h1>
      </div>
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm"
           style={{ background: '#f5f5f7', color: '#6e6e73' }}>
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          placeholder="Search…"
          className="bg-transparent outline-none text-xs w-32"
          style={{ color: '#1d1d1f' }}
        />
      </div>
    </div>
  )
}
