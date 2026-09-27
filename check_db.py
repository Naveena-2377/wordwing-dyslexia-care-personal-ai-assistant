import sys
sys.path.append('src')
from dyslexia.api.db import SessionLocal
from dyslexia.api.models_db import User, ReadingSession

db = SessionLocal()
user = db.query(User).filter(User.email == 'test@test.com').first()
print('User:', user.name, user.email, '| id:', user.id)

sessions = db.query(ReadingSession).filter(ReadingSession.user_id == user.id).all()
print(f'Saved sessions: {len(sessions)}')
for s in sessions:
    print(f'  - {s.created_at} | wpm={s.wpm:.1f} | accuracy={s.accuracy:.2%} | risk={s.risk_band} | text="{s.target_text}"')
db.close()