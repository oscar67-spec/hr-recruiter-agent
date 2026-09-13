import { NextResponse } from 'next/server'
import { listCandidates } from '@/lib/s3'

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const jobId = searchParams.get('job_id') ?? undefined
  try {
    const candidates = await listCandidates(jobId)
    return NextResponse.json(candidates)
  } catch (err) {
    console.error('Candidates API error:', err)
    return NextResponse.json([], { status: 200 })
  }
}
