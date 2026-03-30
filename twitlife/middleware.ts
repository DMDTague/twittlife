import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req: request, res })

  try {
    const {
      data: { session },
    } = await supabase.auth.getSession()

    // If user is not authenticated
    if (!session) {
      // Allow access to public pages
      if (pathname === '/login' || pathname === '/auth/callback') {
        return res
      }
      // Redirect to login for protected pages
      return NextResponse.redirect(new URL('/login', request.url))
    }

    // If user is authenticated but on public pages
    if (pathname === '/login') {
      // Check if they need to create a character
      // (This will be checked by the app, not middleware)
      return NextResponse.redirect(new URL('/create-account', request.url))
    }

    return res
  } catch (error) {
    console.error('Middleware error:', error)
    // On error, redirect to login for safety
    if (pathname !== '/login' && pathname !== '/auth/callback') {
      return NextResponse.redirect(new URL('/login', request.url))
    }
    return res
  }
}

export const config = {
  matcher: [
    // Protect all routes except public ones
    '/((?!.*\\.[a-z]+$|_next).*)',
    // But allow auth pages
    '/login',
    '/auth/callback',
  ],
}
