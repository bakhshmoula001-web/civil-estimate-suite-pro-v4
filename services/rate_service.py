from models.rate_item import RateItem

class RateService:
    def __init__(self, repository):
        self.repository = repository

    def get_by_project(self, project_id):
        return self.repository.get_by_project(project_id)

    def get_rate(self, project_id, category, item_name, unit, default=0.0):
        item = self.repository.find(project_id, category, item_name, unit)
        return float(item.rate) if item else float(default)

    def upsert(self, item):
        item.validate()
        existing = self.repository.find(
            item.project_id, item.category, item.item_name, item.unit
        )
        if existing is None:
            item.id = self.repository.create(item)
            return self.repository.get(item.id)
        self.repository.update(existing.id, item)
        return self.repository.get(existing.id)

    def seed_defaults(self, project_id, defaults):
        return [
            self.upsert(
                RateItem(
                    project_id=int(project_id),
                    category=d["category"],
                    item_name=d["item_name"],
                    unit=d["unit"],
                    rate=float(d["rate"]),
                    source=d.get("source", "Application Default"),
                    remarks=d.get("remarks", ""),
                )
            )
            for d in defaults
        ]
