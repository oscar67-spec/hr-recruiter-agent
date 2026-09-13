'use client'
import { useState } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    const res = await signIn('credentials', { email, password, redirect: false })
    setLoading(false)
    if (res?.ok) router.push('/dashboard')
    else setError('Invalid email or password')
  }

  return (
    <div className="min-h-screen flex" style={{ background: '#f5f5f7' }}>
      {/* Left panel — branding */}
      <div className="hidden lg:flex w-[480px] shrink-0 flex-col justify-between p-12"
           style={{ background: '#1d1d1f' }}>
        <div>
          <div className="flex items-center gap-2.5 mb-16">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                 style={{ background: '#0071e3' }}>
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <span className="text-white font-semibold text-sm">HR Recruiter</span>
          </div>

          <h1 className="text-4xl font-semibold leading-tight mb-4"
              style={{ color: '#f5f5f7' }}>
            Your AI-powered<br />recruiting team.
          </h1>
          <p className="text-base leading-relaxed" style={{ color: '#6e6e73' }}>
            Manage your entire hiring pipeline — from job postings and resume screening to interviews and offers — all through conversation.
          </p>
        </div>

        <div className="space-y-4">
          {[
            { n: '24', label: 'AI-powered tools' },
            { n: '3',  label: 'ATS integrations' },
            { n: '∞',  label: 'Candidates managed' },
          ].map(item => (
            <div key={item.n} className="flex items-center gap-3">
              <span className="text-2xl font-semibold" style={{ color: '#f5f5f7' }}>{item.n}</span>
              <span className="text-sm" style={{ color: '#6e6e73' }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                 style={{ background: '#0071e3' }}>
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <span className="font-semibold text-sm" style={{ color: '#1d1d1f' }}>HR Recruiter</span>
          </div>

          <h2 className="text-2xl font-semibold mb-1" style={{ color: '#1d1d1f' }}>Sign in</h2>
          <p className="text-sm mb-8" style={{ color: '#6e6e73' }}>Enter your credentials to continue</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: '#1d1d1f' }}>
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                placeholder="recruiter@company.com"
                className="w-full px-3 py-2.5 text-sm rounded-lg outline-none transition-all"
                style={{
                  background: '#ffffff',
                  border: '1px solid #d2d2d7',
                  color: '#1d1d1f',
                }}
                onFocus={e => e.target.style.borderColor = '#0071e3'}
                onBlur={e => e.target.style.borderColor = '#d2d2d7'}
              />
            </div>

            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: '#1d1d1f' }}>
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full px-3 py-2.5 text-sm rounded-lg outline-none transition-all"
                style={{
                  background: '#ffffff',
                  border: '1px solid #d2d2d7',
                  color: '#1d1d1f',
                }}
                onFocus={e => e.target.style.borderColor = '#0071e3'}
                onBlur={e => e.target.style.borderColor = '#d2d2d7'}
              />
            </div>

            {error && (
              <p className="text-xs px-3 py-2.5 rounded-lg"
                 style={{ background: '#fee2e2', color: '#ff3b30' }}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg text-sm font-medium transition-opacity disabled:opacity-50"
              style={{ background: '#1d1d1f', color: '#ffffff' }}
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="text-center text-xs mt-8" style={{ color: '#aeaeb2' }}>
            Secured by AWS Bedrock AgentCore
          </p>
        </div>
      </div>
    </div>
  )
}
