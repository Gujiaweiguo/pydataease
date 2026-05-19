import pytest
from httpx import ASGITransport, AsyncClient
from types import SimpleNamespace

from tests.fixtures.db_fixtures import *  # noqa: F401,F403

from app.main import app
from app.dependencies.database import get_db
from app.services.permission_service import get_permission_service
from app.utils.password_utils import hash_password


def _build_user(*, user_id: int, account: str, password: str, oid: int, enable: bool = True, language: str = "zh-CN"):
    return SimpleNamespace(
        id=user_id,
        account=account,
        name=account,
        password=hash_password(password),
        enable=enable,
        oid=oid,
        origin=0,
        language=language,
    )


@pytest.fixture
def fake_auth_users():
    return {
        1: _build_user(user_id=1, account="admin", password="DataEase@123456", oid=1),
        2: _build_user(user_id=2, account="embedded", password="Embedded@123456", oid=3),
        7: _build_user(user_id=7, account="route7", password="Route@123456", oid=9),
        11: _build_user(user_id=11, account="share11", password="Share@123456", oid=13),
    }


class FakePermissionService:
    async def require_resource_access(self, user, resource_type: str, permission_type: str = "use") -> None:
        return None

    async def has_resource_permission(self, user, resource_type: str, permission_type: str = "use") -> bool:
        return True

    async def get_effective_menu_ids(self, user_id: int, oid: int) -> set[int]:
        return set()


@pytest.fixture(autouse=True)
def install_fake_auth_backend(monkeypatch, fake_auth_users):
    import app.dependencies.auth as auth_dependencies
    import app.middleware.auth as auth_middleware
    import app.services.auth_service as auth_service

    class FakeUserRepository:
        def __init__(self, session) -> None:
            self._users = session.users

        async def get_by_id(self, user_id: int):
            return self._users.get(user_id)

        async def get_by_account(self, account: str):
            return next((user for user in self._users.values() if user.account == account), None)

    class FakeOrgRepository:
        def __init__(self, session) -> None:
            self._users = session.users

        def _build_org(self, org_id: int):
            if org_id <= 0:
                return None
            name = "默认组织" if org_id == 1 else f"org-{org_id}"
            return SimpleNamespace(id=org_id, pid=0, name=name)

        async def is_member(self, user_id: int, org_id: int):
            # BUG-042 fix: Accept any valid user_id/oid combo (simulating multi-org)
            return user_id > 0 and org_id > 0

        async def get_user_orgs(self, user_id: int):
            user = self._users.get(user_id)
            if user is None or user.oid <= 0:
                return []
            org = self._build_org(user.oid)
            return [] if org is None else [org]

        async def get_by_id(self, org_id: int):
            return self._build_org(org_id)

    class FakeSession(SimpleNamespace):
        async def rollback(self) -> None:
            return None

        async def execute(self, statement=None, params=None):
            return None

        async def get(self, entity, ident):
            return None

        async def commit(self) -> None:
            return None

        async def flush(self) -> None:
            return None

        async def refresh(self, entity) -> None:
            return None

        def add(self, entity) -> None:
            return None

        async def delete(self, entity) -> None:
            return None

    class FakeSessionContext:
        def __init__(self, session) -> None:
            self._session = session

        async def __aenter__(self):
            return self._session

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    session = FakeSession(users=fake_auth_users)

    async def override_get_db():
        yield session

    monkeypatch.setattr(auth_middleware, "UserRepository", FakeUserRepository)
    monkeypatch.setattr(auth_middleware, "OrgRepository", FakeOrgRepository)
    monkeypatch.setattr(auth_dependencies, "UserRepository", FakeUserRepository)
    monkeypatch.setattr(auth_service, "UserRepository", FakeUserRepository)
    monkeypatch.setattr(auth_service, "OrgRepository", FakeOrgRepository)
    monkeypatch.setattr(auth_middleware, "async_session", lambda: FakeSessionContext(session))
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_permission_service] = lambda: FakePermissionService()
    yield
    _ = app.dependency_overrides.pop(get_db, None)
    _ = app.dependency_overrides.pop(get_permission_service, None)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
