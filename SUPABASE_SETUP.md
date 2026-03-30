# Supabase Setup Guide (Phase 28)

## Quick Start

### 1. Create Supabase Project

```bash
# Option A: Online at https://app.supabase.com
# - Click "New Project"
# - Name: "twitlife"
# - Password: Generate strong password
# - Region: Choose closest to your deployment
# - Wait for DB to initialize (~3 min)

# Option B: Using CLI (Recommended for development)
brew install supabase/tap/supabase  # On macOS
# Windows: choco install supabase-cli
# Linux: Use installation guide

supabase init  # In your project root
supabase login  # Opens browser for authentication
supabase link --project-ref YOUR_PROJECT_REF  # Link to existing project
```

### 2. Set Environment Variables

Create `.env.local` in your Next.js project:

```env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...  # Public key from Supabase dashboard
```

Create `.env` in `backend/`:

```env
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...  # Service role key (private)
DATABASE_URL=postgresql://postgres:PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres
```

### 3. Deploy Schema

#### Option A: Using Supabase CLI (Development)

```bash
cd backend/migrations
supabase db push
```

#### Option B: Using Supabase Dashboard (Production)

1. Go to SQL Editor
2. Create new query
3. Copy-paste content of `001_phase28_schema.sql`
4. Click "Execute"

### 4. Configure Authentication (Google OAuth + Email)

**In Supabase Dashboard:**

1. Go to **Settings → Authentication**
2. Configure **Email Provider**:
   - Enable "Email confirmation"
   - Email template: Use defaults or customize
3. Configure **Google OAuth**:
   - Go to Google Cloud Console: https://console.cloud.google.com
   - Create OAuth 2.0 credentials (Web application)
   - Set Redirect URI: `https://YOUR_PROJECT_ID.supabase.co/auth/v1/callback`
   - Copy Client ID + Client Secret
   - In Supabase, paste into Google provider section

### 5. Test Connection

**Backend:**
```bash
cd backend
python -c "
import os
from supabase import create_client
import dotenv

dotenv.load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

# Test connection
result = supabase.table('accounts').select('*').execute()
print(f'✓ Connected. Found {len(result.data)} accounts')
"
```

**Frontend:**
```bash
cd twitlife
npm run dev
# Open http://localhost:3000/login
# Verify Supabase loads without errors
```

### 6. Install Dependencies

**Backend:**
```bash
cd backend
pip install supabase python-dotenv
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd twitlife
npm install @supabase/supabase-js @supabase/auth-ui-react @supabase/auth-ui-shared
```

## Supabase Project Reference

| Item | Value |
|------|-------|
| Project ID | _(from dashboard)_ |
| Anon Key | _(from Settings → API)_ |
| Service Key | _(from Settings → API - keep secret!)_ |
| Database URL | _(auto-generated)_ |
| API URL | `https://YOUR_PROJECT_ID.supabase.co` |

## Useful Links

- Supabase Docs: https://supabase.com/docs
- Python Client: https://github.com/supabase/supabase-py
- JS Client: https://github.com/supabase/supabase-js
- Dashboard: https://app.supabase.com
- CLI: https://supabase.com/docs/guides/cli
