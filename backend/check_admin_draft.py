from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Draft, LeagueUser

engine = create_engine("sqlite:///./fantasyduel.db")
Session = sessionmaker(bind=engine)
db = Session()

# Get admin's draft
admin_league_user = db.query(LeagueUser).filter_by(user_id="admin-user").first()
draft = db.query(Draft).filter_by(pair_id=admin_league_user.pair_id).first()

print("Admin can now access the draft room!")
print(f"Draft URL: http://localhost:3000/draft/{draft.id}")
print(f"Status: {draft.status}")
print("Admin is the current picker!")

# Get opponent
opponent = (
    db.query(LeagueUser)
    .filter(
        LeagueUser.pair_id == admin_league_user.pair_id,
        LeagueUser.user_id != "admin-user",
    )
    .first()
)
print(f"Opponent: {opponent.display_name}")

db.close()
