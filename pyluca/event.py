import datetime


class Event:
    def __init__(
            self,
            event_id: str,
            date: datetime.datetime,
            created_date: datetime.datetime,
            created_by: str = None
    ):
        self.event_id = event_id
        self.date = date
        self.created_date = created_date
        self.created_by = created_by
