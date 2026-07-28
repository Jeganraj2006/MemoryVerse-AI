import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.error(
    '[MemoryVerse] Missing Supabase env vars. ' +
    'Create frontend/.env with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY. ' +
    'See frontend/.env.example for reference.'
  )
}

// Use placeholder values when env vars are missing so the app renders
// (it will show auth errors on sign-in, not a blank white crash)
export const supabase = createClient(
  supabaseUrl  || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder-anon-key',
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  }
)

