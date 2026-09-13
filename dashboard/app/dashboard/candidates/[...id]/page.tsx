import { getCandidate } from '@/lib/s3'
import { ScoreBadge, RecBadge } from '@/components/Badges'
import Link from 'next/link'
import { ArrowLeft, Mail, Briefcase, Star, AlertCircle, FileText } from 'lucide-react'
import { notFound } from 'next/navigation'

export const dynamic = 'force-dynamic'

export default async function CandidateDetailPage({
  params,
}: {
  params: Promise<{ id: string[] }>
}) {
  const { id } = await params
  const [jobId, candidateId] = id ?? []
  if (!jobId || !candidateId) notFound()

  let candidate: any
  try {
    candidate = await getCandidate(jobId, candidateId)
  } catch {
    notFound()
  }

  return (
    <div className="p-6 max-w-3xl">
      <Link
        href="/dashboard/candidates"
        className="inline-flex items-center gap-1.5 text-xs mb-6 transition-colors"
        style={{ color: '#6e6e73' }}
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Candidates
      </Link>

      {/* Header */}
      <div className="card p-6 mb-4">
        <div className="flex items-start justify-between flex-wrap gap-4 mb-5">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full flex items-center justify-center text-lg font-semibold shrink-0"
                 style={{ background: '#f5f5f7', color: '#1d1d1f' }}>
              {candidate.candidate_name?.[0]?.toUpperCase() ?? 'C'}
            </div>
            <div>
              <p className="text-base font-semibold" style={{ color: '#1d1d1f' }}>
                {candidate.candidate_name}
              </p>
              <a href={`mailto:${candidate.candidate_email}`}
                 className="flex items-center gap-1 text-xs mt-0.5"
                 style={{ color: '#0071e3' }}>
                <Mail className="w-3 h-3" />
                {candidate.candidate_email}
              </a>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ScoreBadge score={candidate.score} />
            <RecBadge rec={candidate.recommendation} />
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-5"
             style={{ borderTop: '1px solid #f5f5f7' }}>
          <InfoItem icon={Briefcase} label="Role"   value={candidate.role} />
          <InfoItem icon={Star}      label="Score"  value={`${candidate.score ?? 'N/A'}/100`} />
          <InfoItem icon={Mail}      label="Status" value={candidate.status} />
        </div>
      </div>

      {/* Strengths & Gaps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3">
            <Star className="w-3.5 h-3.5" style={{ color: '#34c759' }} />
            <p className="text-sm font-medium" style={{ color: '#1d1d1f' }}>Strengths</p>
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-line" style={{ color: '#6e6e73' }}>
            {candidate.strengths ?? 'No data'}
          </p>
        </div>
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-3.5 h-3.5" style={{ color: '#ff9f0a' }} />
            <p className="text-sm font-medium" style={{ color: '#1d1d1f' }}>Gaps</p>
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-line" style={{ color: '#6e6e73' }}>
            {candidate.gaps ?? 'No data'}
          </p>
        </div>
      </div>

      {/* Summary */}
      {candidate.summary && (
        <div className="card p-5 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-3.5 h-3.5" style={{ color: '#6e6e73' }} />
            <p className="text-sm font-medium" style={{ color: '#1d1d1f' }}>AI Summary</p>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: '#6e6e73' }}>{candidate.summary}</p>
        </div>
      )}

      {/* Actions */}
      <div className="card p-5">
        <p className="text-sm font-medium mb-4" style={{ color: '#1d1d1f' }}>Actions</p>
        <div className="flex flex-wrap gap-3">
          <a
            href={`mailto:${candidate.candidate_email}?subject=Interview Invitation - ${candidate.role}`}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-opacity hover:opacity-80"
            style={{ background: '#1d1d1f', color: '#ffffff' }}
          >
            Send Interview Invite
          </a>
          <Link
            href="/dashboard/candidates"
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{ background: '#f5f5f7', color: '#1d1d1f' }}
          >
            All Candidates
          </Link>
        </div>
      </div>
    </div>
  )
}

function InfoItem({ icon: Icon, label, value }: { icon: any; label: string; value?: string }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className="w-3 h-3" style={{ color: '#aeaeb2' }} />
        <span className="text-xs" style={{ color: '#aeaeb2' }}>{label}</span>
      </div>
      <p className="text-sm font-medium capitalize" style={{ color: '#1d1d1f' }}>{value ?? 'N/A'}</p>
    </div>
  )
}
