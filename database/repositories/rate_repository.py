from models.rate_item import RateItem

class RateRepository:
    def __init__(self, database):
        self.db = database

    def create(self, item):
        cur = self.db.execute(
            """INSERT INTO rate_items
            (project_id, category, item_name, unit, rate, source, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (item.project_id, item.category, item.item_name, item.unit,
             item.rate, item.source, item.remarks),
        )
        self.db.commit()
        return cur.lastrowid

    def get(self, rate_id):
        return RateItem.from_row(
            self.db.fetchone("SELECT * FROM rate_items WHERE id=?", (rate_id,))
        )

    def get_by_project(self, project_id):
        rows = self.db.fetchall(
            """SELECT * FROM rate_items
               WHERE project_id=?
               ORDER BY category, item_name, unit""",
            (project_id,),
        )
        return [RateItem.from_row(row) for row in rows]

    def find(self, project_id, category, item_name, unit):
        row = self.db.fetchone(
            """SELECT * FROM rate_items
               WHERE project_id=?
               AND LOWER(TRIM(category))=LOWER(TRIM(?))
               AND LOWER(TRIM(item_name))=LOWER(TRIM(?))
               AND LOWER(TRIM(unit))=LOWER(TRIM(?))
               LIMIT 1""",
            (project_id, category, item_name, unit),
        )
        return RateItem.from_row(row)

    def update(self, rate_id, item):
        self.db.execute(
            """UPDATE rate_items
               SET category=?, item_name=?, unit=?, rate=?,
                   source=?, remarks=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (item.category, item.item_name, item.unit, item.rate,
             item.source, item.remarks, rate_id),
        )
        self.db.commit()
        return True
