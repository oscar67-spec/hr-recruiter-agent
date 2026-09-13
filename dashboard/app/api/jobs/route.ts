import { NextResponse } from 'next/server'
import { listJobs } from '@/lib/s3'

export async function GET() {
  try {
    const jobs = await listJobs()
    return NextResponse.json(jobs)
  } catch (err) {
    console.error('Jobs API error:', err)
    return NextResponse.json([], { status: 200 })
  }
}
