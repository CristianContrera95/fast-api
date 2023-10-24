from app.sqlserverdb import SessionLocal

db = SessionLocal()

#####
# Example:
# Add column organization_id on account table and make a foreign key to id in organization table
#
#####
#
# db.execute("ALTER TABLE account ADD organization_id int NOT NULL DEFAULT(1)")
# db.execute("ALTER TABLE account ADD CONSTRAINT organization_id FOREIGN KEY(organization_id) REFERENCES organization(id)")
