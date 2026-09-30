# mini_kit

Versione ridotta del kit interno con cui Klaaryo scrive i propri servizi Django, preparata per il
technical assessment. Non è il kit di produzione: ne conserva le convenzioni (view sottili, logica
nei manager, dati separati per team, token che identifica chi chiama) in poche centinaia di righe.

Leggerlo è parte dell'assessment: ogni modulo è breve e fa una cosa sola.

## Cosa contiene

| Modulo | Cosa fa |
|---|---|
| `mini_kit.models` | `KitBaseModel` (`created_at`, `updated_at`) e `TeamScopedModel` (`team_pk` + classmethod `for_team(team_pk)`) |
| `mini_kit.managers` | `BaseManager(team_pk, user_pk)`: la base dei REST manager, con `_validate_payload()` |
| `mini_kit.views` | `BaseApiView`: costruisce il manager dal token e restituisce le risposte (`respond_item`, `respond_created`, `respond_list`) |
| `mini_kit.errors` | `KitError` e le sottoclassi `InvalidPayloadError` (400), `NotFoundError` (404), `ConflictError` (409) |
| `mini_kit.exception_handler` | Trasforma ogni errore nel formato standard `{"error": {"code", "message"}}` |
| `mini_kit.auth` | Token JWT con `user_pk` e `team_pk`, autenticazione DRF, comando `issue_token` |
| `mini_kit.testing` | `KitAPITestCase` con `as_user()` e `assert_error()` |

## Installazione

Il kit è una dipendenza del servizio, dichiarata in `requirements.txt`:

```
mini_kit @ git+https://github.com/zwapin/mini_kit.git@v0.1.0
```

`pip` lo scarica da GitHub, quindi dove lanci `pip install` serve `git`. Un servizio di esempio che
usa il kit è [applications_service_starter](https://github.com/zwapin/applications_service_starter).

## Setup nel servizio

```python
# settings.py
from mini_kit.settings import REST_FRAMEWORK

INSTALLED_APPS = [
    "rest_framework",
    "mini_kit",
    # ... le app del servizio
]

MINI_KIT_JWT_SECRET = os.environ["MINI_KIT_JWT_SECRET"]
```

```python
# urls.py (root)
handler404 = "mini_kit.views.not_found_view"
handler500 = "mini_kit.views.server_error_view"
```

`handler404` e `handler500` valgono solo con `DEBUG = False`: con `DEBUG = True` Django mostra la
sua pagina di debug per le route che non esistono.

## I layer

```
rest_apis/views/     → view sottili: leggono la richiesta, chiamano il REST manager, restituiscono la risposta
rest_apis/managers/  → REST manager (BaseManager): validano l'input API e delegano ai core manager
rest_apis/serializers/ → serializer di input e di output
managers/            → core manager: logica di dominio, a scatola nera da dati a risultati
django_db_models/    → modelli Django, un file per modello in models/
```

Il core manager non conosce HTTP né JSON: riceve dati Python, restituisce modelli o queryset, e
solleva un errore del kit quando qualcosa non va. Nessun file sotto `rest_apis/` importa da
`django_db_models/` e nessuna regola di dominio sta sotto `rest_apis/`.

### Modelli

```python
from mini_kit.models import TeamScopedModel


class NoteModel(TeamScopedModel):
    title = models.CharField(max_length=100)
```

Tutto quello che appartiene a un team eredita da `TeamScopedModel`. Le query partono sempre da
`NoteModel.for_team(self.team_pk)`, mai da `NoteModel.objects`, che non è filtrato per team.

### Core manager (`managers/`)

```python
from django.apps import apps

from mini_kit.errors import NotFoundError


class NoteNotFoundError(NotFoundError):
    code = "note_not_found"
    default_message = "Note not found"


class NoteManager:

    def __init__(self, team_pk: int):
        self._team_pk = team_pk

    def get_note(self, note_pk: int) -> "NoteModel":
        note = apps.get_model("django_db_models", "NoteModel").for_team(self._team_pk).filter(pk=note_pk).first()
        if note is None:
            raise NoteNotFoundError()
        return note
```

- Gli errori di dominio si **sollevano** come sottoclassi di `KitError`, con un `code` proprio.
  Non si restituiscono `None` o `False`.
- Il core manager si usa e si testa senza API: `NoteManager(team_pk=1).get_note(3)`.

### REST manager (`rest_apis/managers/`)

```python
from mini_kit.managers import BaseManager


class NoteApiManager(BaseManager):

    def create_note(self, payload: dict) -> "NoteModel":
        data = self._validate_payload(NoteInputSerializer, payload)
        return NoteManager(team_pk=self.team_pk).create_note(title=data["title"])
```

- `self.team_pk` e `self.user_pk` arrivano dal token: non si leggono mai da body o query string.
- `_validate_payload()` esegue un serializer DRF. Se il payload non è valido, il kit risponde
  `400 invalid_payload` indicando il primo campo che non va.

### View (`rest_apis/views/`)

```python
from mini_kit.views import BaseApiView
from rest_apis.managers import NoteApiManager
from rest_apis.serializers import NoteSerializerModel


class NotesApiView(BaseApiView):
    manager_class = NoteApiManager

    def post(self, request):
        return self.respond_created(self.manager.create_note(request.data), NoteSerializerModel)
```

`self.manager` è un'istanza di `manager_class` già legata al team e all'utente del token.
`respond_list` restituisce `{"count": N, "results": [...]}` con `200`, anche quando la lista è vuota.

## Errori

Tutte le risposte di errore hanno questa forma:

```json
{"error": {"code": "note_not_found", "message": "Note not found"}}
```

| Origine | Status | `code` |
|---|---|---|
| Sottoclasse di `KitError` sollevata da un manager | quello della classe | quello della classe |
| Serializer non valido, JSON malformato | 400 | `invalid_payload` |
| Token mancante, malformato, scaduto o con firma errata | 401 | `unauthorized` |
| Route inesistente | 404 | `not_found` |
| Metodo HTTP non gestito dalla view | 405 | `method_not_allowed` |
| Qualsiasi altra eccezione (viene loggata) | 500 | `internal_error` |

## Autenticazione

Ogni richiesta porta l'header:

```
Authorization: Token <jwt>
```

Il token è un JWT firmato HS256 con `MINI_KIT_JWT_SECRET`, che contiene due claim: `user_pk` e
`team_pk`. Il kit lo verifica e lo trasforma in `request.user`, un `AuthenticatedUser(user_pk, team_pk)`.

Per generare un token per un utente di un team:

```bash
python manage.py issue_token --user-pk 10 --team-pk 1
python manage.py issue_token --user-pk 10 --team-pk 1 --expires-in-hours 24
```

Senza `--expires-in-hours` il token non scade.

## Test

```python
from mini_kit.testing import KitAPITestCase


class NoteApiTest(KitAPITestCase):

    def test_other_team_note_is_not_found(self):
        note = NoteModel.objects.create(team_pk=1, title="Team 1 note")
        self.as_user(team_pk=2)

        response = self.client.get(f"/api/v1/notes/{note.pk}")

        self.assert_error(response, 404, "note_not_found")
```

`as_user()` genera un token vero: i test passano dall'autenticazione reale, non la aggirano.

## Sviluppo del kit

```bash
python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]"
DJANGO_SETTINGS_MODULE=tests.settings .venv/bin/python -m django test tests
# Postgres invece di SQLite:
DB_HOST=127.0.0.1 DB_PORT=55432 DJANGO_SETTINGS_MODULE=tests.settings .venv/bin/python -m django test tests
```

## Licenza

MIT, vedi [LICENSE](LICENSE).
