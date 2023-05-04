import datetime
from typing import List, Optional


class JournalEntry:
    """
    A struct for individual journal entry.

    :param sl_no: sl_no of the entry (starting from 1)
    :param account: The account which the entry is passed for
    :param dr_amount: Debit amount
    :param cr_amount: Credit amount
    :param date: Time of occurrence
    :param narration: A narration or description for the entry
    :param key: A key to group the journal entries
    :param event_id: Identifier for event caused this entry
    """
    def __init__(
            self, sl_no: int,
            account: str,
            dr_amount: float,
            cr_amount: float,
            date: datetime.datetime,
            narration: str,
            key: str,
            event_id: Optional[str]
    ):
        self.sl_no = sl_no
        self.account = account
        self.dr_amount = dr_amount
        self.cr_amount = cr_amount
        self.date = date
        self.narration = narration
        self.key = key
        self.event_id = event_id


class Journal:
    """
    A log which maintains list of journal entries.

    :param entries: An optional opening journal entries
    """
    def __init__(self, entries: List[JournalEntry] = None):
        self.entries: List[JournalEntry] = [] if entries is None else entries
        self.max_date: datetime = max([entry.date for entry in entries]) if entries else None

    def add_entry(self, entry: JournalEntry):
        """
        Function which takes an entry and adds to the entries after validation on date. Raises
        exception if passed entry is back dated

        :param entry: Entry to be added
        :raises: AssertionError
        """
        if self.max_date is None:
            self.max_date = entry.date
        assert entry.date >= self.max_date, \
            f'Backdated entries cannot be added for entry_date: {entry.date.strftime("%d-%m-%Y %H:%M:%S")} and max_date: {self.max_date.strftime("%d-%m-%Y %H:%M:%S")}'
        self.entries.append(entry)
        self.max_date = entry.date
