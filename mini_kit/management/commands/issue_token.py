# IMPORTING STANDARD PACKAGES
from datetime import timedelta

# IMPORTING THIRD PARTY PACKAGES
from django.core.management.base import BaseCommand, CommandParser

# IMPORTING LOCAL PACKAGES
from mini_kit.auth.tokens import issue_token


class Command(BaseCommand):
    """Usage: python manage.py issue_token --user-pk 10 --team-pk 1 [--expires-in-hours 24]"""

    help = "Issue a signed token for a user of a team"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--user-pk", type=int, required=True)
        parser.add_argument("--team-pk", type=int, required=True)
        parser.add_argument("--expires-in-hours", type=int, help="Omit for a token that never expires")

    def handle(self, *args, **options) -> None:
        expires_in_hours = options["expires_in_hours"]
        expires_in = timedelta(hours=expires_in_hours) if expires_in_hours is not None else None
        self.stdout.write(issue_token(user_pk=options["user_pk"], team_pk=options["team_pk"], expires_in=expires_in))
