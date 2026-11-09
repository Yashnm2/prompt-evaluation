from datetime import datetime, timedelta, timezone
from operator import itemgetter


def deals_needing_followup(deals, today=None):
    """Return open deals with contacts older than 14 days, oldest first.

    Never-contacted deals come first. Exactly 14 days does not qualify.
    Contact timestamps and an explicitly supplied today must have timezones.
    Equal contact times retain input order.
    """
    if today is None:
        today = datetime.now(timezone.utc)
    if today.utcoffset() is None:
        raise ValueError("today must include a timezone")
    today = today.astimezone(timezone.utc)

    followup_interval = timedelta(days=14)
    stale_contacts = []
    earliest_contact = datetime.min.replace(tzinfo=timezone.utc)

    for deal in deals:
        if deal["stage"].startswith("Closed"):
            continue

        # Handle missing contacts before parsing or comparing datetimes.
        if deal["last_contact"] is None:
            stale_contacts.append((earliest_contact, deal["name"]))
            continue

        last_contact = datetime.fromisoformat(deal["last_contact"])
        if last_contact.utcoffset() is None:
            raise ValueError("last_contact must include a timezone")
        # Compare and sort actual instants, including across timezone offsets.
        last_contact = last_contact.astimezone(timezone.utc)

        # Keep the full duration so 14 days plus any fraction qualifies.
        if today - last_contact > followup_interval:
            stale_contacts.append((last_contact, deal["name"]))

    # Each pair stores its UTC contact time at index 0.
    stale_contacts.sort(key=itemgetter(0))
    return [name for last_contact, name in stale_contacts]
