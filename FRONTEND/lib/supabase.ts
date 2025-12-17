import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://klhdatzliltkqvrpbnry.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtsaGRhdHpsaWx0a3F2cnBibnJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUwOTYwNjgsImV4cCI6MjA4MDY3MjA2OH0.Duh3NyHGVO2wvl2klEJo8rXEp8HxV2F9FL0VB3jCyDU'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

