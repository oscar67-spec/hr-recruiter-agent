'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { signOut } from 'next-auth/react'
import { LayoutDashboard, Briefcase, Users, GitBranch, LogOut } from 'lucide-react'

const nav = [
  { href: '/dashboard',            icon: LayoutDashboard, label: 'Overview'   },
  { href: '/dashboard/jobs',       icon: Briefcase,        label: 'Jobs'       },
  { href: '/dashboard/candidates', icon: Users,            label: 'Candidates' },
  { href: '/dashboard/pipeline',   icon: GitBranch,        label: 'Pipeline'   },
]

export default function Sidebar({ user }: { user?: { name?: string | null; email?: string | null } }) {
  const path = usePathname()

  return (
    <aside className="w-56 shrink-0 flex flex-col h-full"
           style={{ background: '#ffffff', boxShadow: '1px 0 0 #d2d2d7' }}>

      {/* Logo */}
      <div className="px-5 py-5" style={{ borderBottom: '1px solid #f5f5f7' }}>
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
               style={{ background: '#1d1d1f' }}>
            <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <p className="text-xs font-semibold leading-none" style={{ color: '#1d1d1f' }}>HR Recruiter</p>
            <p className="text-xs mt-0.5" style={{ color: '#aeaeb2' }}>AI Dashboard</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-2 space-y-0.5">
        {nav.map(({ href, icon: Icon, label }) => {
          const active = path === href || (href !== '/dashboard' && path.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors"
              style={{
                background: active ? '#f5f5f7' : 'transparent',
                color: active ? '#1d1d1f' : '#6e6e73',
                fontWeight: active ? 500 : 400,
              }}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* User */}
      <div className="px-2 py-3" style={{ borderTop: '1px solid #f5f5f7' }}>
        <div className="px-3 py-2 mb-0.5">
          <p className="text-xs font-medium truncate" style={{ color: '#1d1d1f' }}>
            {user?.name ?? 'Recruiter'}
          </p>
          <p className="text-xs truncate" style={{ color: '#aeaeb2' }}>{user?.email}</p>
        </div>
        <button
          onClick={() => signOut({ callbackUrl: '/login' })}
          className="flex items-center gap-2 px-3 py-2 rounded-lg w-full text-xs transition-colors"
          style={{ color: '#6e6e73' }}
          onMouseEnter={e => (e.currentTarget.style.background = '#f5f5f7')}
          onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
