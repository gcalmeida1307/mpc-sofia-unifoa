export type AuthUser = {
  user_code: string
  email: string
  name: string
  role: string
  scopes: string[]
  must_change_password: boolean
  two_factor_enabled?: boolean
  active?: boolean
  last_login_at?: string | null
  last_seen_at?: string | null
  blocked_at?: string | null
  blocked_reason?: string | null
}

export type AccessRequest = {
  id: number
  request_code: string
  requested_module?: string
  email: string
  name: string
  requested_scopes: string[]
  status: string
  created_at: string
}

export type AdminUser = AuthUser & {
  session_count: number
  tokens: Array<{
    fingerprint: string
    created_at: string
    last_seen_at?: string | null
    last_rotated_at?: string | null
    expires_at: number
    rotation_seconds: number
  }>
}
