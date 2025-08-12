import os
import numpy as np
import SupabaseManager

isProd = False
supabase = SupabaseManager.get_supabase_client(isProd= isProd)

print("test")