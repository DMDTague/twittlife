import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Middleware — Arcade mode (no auth checks).
 * All routes are public. Character state is managed client-side via localStorage.
 */
export function middleware(request: NextRequest) {
  return NextResponse.next()
}

export const config = {
  matcher: [],
}
