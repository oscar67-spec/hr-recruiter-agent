import { NextResponse } from 'next/server'

export async function POST(req: Request) {
  const { prompt, sessionId } = await req.json()

  const runtimeUrl = process.env.AGENTCORE_RUNTIME_URL!
  const res = await fetch(runtimeUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.AGENTCORE_TOKEN ?? ''}`,
    },
    body: JSON.stringify({ prompt, session_id: sessionId }),
  })

  const data = await res.json()
  const text = data?.content?.[0]?.text ?? data?.response ?? JSON.stringify(data)
  return NextResponse.json({ response: text })
}
