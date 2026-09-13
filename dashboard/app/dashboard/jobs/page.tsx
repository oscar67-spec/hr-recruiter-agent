import { listJobs } from '@/lib/s3'
import Link from 'next/link'
import { MapPin, Clock, Users, Briefcase } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function JobsPage() {
  const jobs = await listJobs()
  return (
    <div className="p-6">
      <div className="mb-5">
        <p className="text-base font-semibold" style={{ color: '#1d1d1f' }}>Jobs</p>
        <p className="text-xs mt-0.5" style={{ color: '#aeaeb2' }}>
          {jobs.length} role{jobs.length !== 1 ? 's' : ''}
        </p>
      </div>

      {jobs.length === 0 ? (
        <div className="card p-16 text-center">
          <Briefcase className="w-8 h-8 mx-auto mb-3" style={{ color: '#d2d2d7' }} />
          <p className="text-sm font-medium" style={{ color: '#6e6e73' }}>No job postings yet</p>
          <p className="text-xs mt-1" style={{ color: '#aeaeb2' }}>Ask the HR agent to create one</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {jobs.map((job: any, i) => (
            <div key={i} className="card p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                     style={{ background: '#f5f5f7' }}>
                  <Briefcase className="w-4 h-4" style={{ color: '#6e6e73' }} />
                </div>
                <span className="text-xs font-medium px-2.5 py-1 rounded-full"
                      style={job.status === 'open'
                        ? { background: '#d1fae5', color: '#059669' }
                        : { background: '#f5f5f7', color: '#6e6e73' }}>
                  {job.status ?? 'open'}
                </span>
              </div>

              <p className="text-sm font-medium mb-0.5" style={{ color: '#1d1d1f' }}>
                {job.role ?? 'Untitled Role'}
              </p>
              <p className="text-xs mb-4" style={{ color: '#6e6e73' }}>{job.department ?? 'N/A'}</p>

              <div className="space-y-1.5 mb-4">
                <div className="flex items-center gap-1.5 text-xs" style={{ color: '#aeaeb2' }}>
                  <MapPin className="w-3 h-3 shrink-0" />
                  {job.location ?? 'Remote'}
                </div>
                <div className="flex items-center gap-1.5 text-xs" style={{ color: '#aeaeb2' }}>
                  <Clock className="w-3 h-3 shrink-0" />
                  {job.employment_type ?? 'Full-time'}
                </div>
                <div className="flex items-center gap-1.5 text-xs" style={{ color: '#aeaeb2' }}>
                  <Clock className="w-3 h-3 shrink-0" />
                  {job.created_at ? new Date(job.created_at).toLocaleDateString() : 'N/A'}
                </div>
              </div>

              <Link href={`/dashboard/candidates?job_id=${job.job_id}`}
                    className="flex items-center gap-1.5 text-xs font-medium"
                    style={{ color: '#0071e3' }}>
                <Users className="w-3 h-3" /> View candidates
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
