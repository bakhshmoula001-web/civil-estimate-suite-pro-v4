from models.rate_item import RateItem

class RateController:
    def __init__(self, service):
        self.service = service

    def get_by_project(self, project_id):
        return self.service.get_by_project(project_id)

    def get_rate(self, project_id, category, item_name, unit, default=0.0):
        return self.service.get_rate(
            project_id, category, item_name, unit, default
        )

    def save(
        self, project_id, category, item_name, unit,
        rate, source="Project", remarks=""
    ):
        item = RateItem(
            project_id=int(project_id),
            category=str(category).strip(),
            item_name=str(item_name).strip(),
            unit=str(unit).strip(),
            rate=float(rate),
            source=str(source).strip() or "Project",
            remarks=str(remarks or "").strip(),
        )
        return self.service.upsert(item)

    def seed_defaults(self, project_id, defaults):
        return self.service.seed_defaults(int(project_id), defaults)
