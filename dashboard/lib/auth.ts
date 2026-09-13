import type { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email:    { label: 'Email',    type: 'email'    },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        // Simple credential check against env vars
        // Add more users by extending this logic or connecting a database
        const validEmail    = process.env.DASHBOARD_EMAIL    ?? 'admin@hr.com'
        const validPassword = process.env.DASHBOARD_PASSWORD ?? 'recruiter123'

        if (
          credentials?.email    === validEmail &&
          credentials?.password === validPassword
        ) {
          return {
            id:    '1',
            name:  'HR Recruiter',
            email: validEmail,
          }
        }
        return null
      },
    }),
  ],
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
    maxAge:   8 * 60 * 60, // 8 hours
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) token.user = user
      return token
    },
    async session({ session, token }) {
      session.user = token.user as typeof session.user
      return session
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
}
