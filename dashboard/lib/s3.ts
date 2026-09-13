import {
  S3Client,
  ListObjectsV2Command,
  GetObjectCommand,
} from '@aws-sdk/client-s3'

const s3 = new S3Client({
  region: process.env.AWS_REGION ?? 'us-east-1',
  credentials: process.env.AWS_ACCESS_KEY_ID ? {
    accessKeyId:     process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    // sessionToken only set if present (SSO/temp creds) — omit for permanent IAM keys
    ...(process.env.AWS_SESSION_TOKEN ? { sessionToken: process.env.AWS_SESSION_TOKEN } : {}),
  } : undefined,  // falls back to default credential chain if no keys set
})

const BUCKET = process.env.HR_S3_BUCKET ?? 'hr-recruiter-agent-data'
const PREFIX = process.env.HR_S3_PREFIX  ?? 'hr-agent'

async function readJson(key: string): Promise<Record<string, unknown>> {
  const res = await s3.send(new GetObjectCommand({ Bucket: BUCKET, Key: key }))
  const text = await res.Body?.transformToString()
  return JSON.parse(text ?? '{}')
}

export async function listJobs(): Promise<Record<string, unknown>[]> {
  const res = await s3.send(new ListObjectsV2Command({
    Bucket: BUCKET,
    Prefix: `${PREFIX}/jobs/`,
  }))
  const keys = (res.Contents ?? []).map(o => o.Key!).filter(k => k.endsWith('.json'))
  const jobs = await Promise.all(keys.map(k => readJson(k)))
  return jobs.sort((a: any, b: any) =>
    new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime()
  )
}

export async function listCandidates(jobId?: string): Promise<Record<string, unknown>[]> {
  const prefix = jobId
    ? `${PREFIX}/candidates/${jobId}/`
    : `${PREFIX}/candidates/`
  const res = await s3.send(new ListObjectsV2Command({ Bucket: BUCKET, Prefix: prefix }))
  const keys = (res.Contents ?? []).map(o => o.Key!).filter(k => k.endsWith('.json'))
  const candidates = await Promise.all(keys.map(k => readJson(k)))
  return candidates.sort((a: any, b: any) => (b.score ?? 0) - (a.score ?? 0))
}

export async function getCandidate(jobId: string, candidateId: string) {
  return readJson(`${PREFIX}/candidates/${jobId}/${candidateId}.json`)
}
