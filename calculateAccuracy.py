import os
import numpy as np
from SupabaseManager import get_supabase_client

isProd = False
supabase = get_supabase_client(isProd= isProd)

print(f"{supabase}")
