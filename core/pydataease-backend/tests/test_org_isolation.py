# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.schemas.auth import TokenUser
from app.services.org_service import OrgService


class FakeOrgRepo:
    """Minimal fake repository for org_service.tree() tests."""

    def __init__(
        self,
        all_orgs: list[SimpleNamespace] | None = None,
        user_orgs: dict[int, list[SimpleNamespace]] | None = None,
    ) -> None:
        self._all_orgs = all_orgs or []
        self._user_orgs = user_orgs or {}

    async def list_all(self) -> list[SimpleNamespace]:
        return self._all_orgs

    async def get_user_orgs(self, user_id: int) -> list[SimpleNamespace]:
        return self._user_orgs.get(user_id, [])


def _org(oid: int, pid: int | None = 0, name: str = "") -> SimpleNamespace:
    return SimpleNamespace(id=oid, pid=pid, name=name or f"org-{oid}")


def _collect_ids(tree: list[dict]) -> set[str]:
    """Recursively collect all non-root node IDs from a tree response."""
    ids: set[str] = set()

    def _walk(nodes: list[dict]) -> None:
        for node in nodes:
            if node.get("id") and node["id"] != "0":
                ids.add(node["id"])
            _walk(node.get("children", []))

    _walk(tree)
    return ids


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_sees_all_orgs() -> None:
    """Admin (user_id=1) sees every organization in the full tree."""
    orgs = [_org(100, 0, "root-org"), _org(200, 100, "child-a"), _org(300, 100, "child-b")]
    repo = FakeOrgRepo(all_orgs=orgs)
    svc = OrgService(session=object(), repository=repo)  # type: ignore[arg-type]

    admin = TokenUser(user_id=1, oid=1)
    tree = [n.model_dump() for n in await svc.tree(admin)]
    ids = _collect_ids(tree)

    assert ids == {"100", "200", "300"}


@pytest.mark.asyncio
async def test_non_admin_sees_only_own_org() -> None:
    """Non-admin sees only the org they belong to — no parent, no children."""
    parent = _org(100, 0, "parent")
    own = _org(200, 100, "own-org")
    child = _org(300, 200, "child-of-own")

    repo = FakeOrgRepo(
        all_orgs=[parent, own, child],
        user_orgs={42: [own]},
    )
    svc = OrgService(session=object(), repository=repo)  # type: ignore[arg-type]

    user = TokenUser(user_id=42, oid=200)
    tree = [n.model_dump() for n in await svc.tree(user)]
    ids = _collect_ids(tree)

    # Must NOT include parent (100) or child (300)
    assert ids == {"200"}


@pytest.mark.asyncio
async def test_non_admin_multiple_orgs_no_ancestors_or_descendants() -> None:
    """User belonging to multiple orgs sees each one but no ancestors/descendants."""
    grandparent = _org(10, 0, "grandparent")
    parent_a = _org(20, 10, "parent-a")
    org_a = _org(30, 20, "org-a")
    parent_b = _org(40, 10, "parent-b")
    org_b = _org(50, 40, "org-b")
    child_of_a = _org(60, 30, "child-of-a")

    repo = FakeOrgRepo(
        all_orgs=[grandparent, parent_a, org_a, parent_b, org_b, child_of_a],
        user_orgs={99: [org_a, org_b]},
    )
    svc = OrgService(session=object(), repository=repo)  # type: ignore[arg-type]

    user = TokenUser(user_id=99, oid=30)
    tree = [n.model_dump() for n in await svc.tree(user)]
    ids = _collect_ids(tree)

    # Only the user's own orgs — no ancestors (10, 20, 40) and no descendants (60)
    assert ids == {"30", "50"}


@pytest.mark.asyncio
async def test_non_admin_no_orgs_returns_empty_tree() -> None:
    """User with no org memberships gets an empty tree."""
    repo = FakeOrgRepo(
        all_orgs=[_org(100, 0, "root")],
        user_orgs={55: []},
    )
    svc = OrgService(session=object(), repository=repo)  # type: ignore[arg-type]

    user = TokenUser(user_id=55, oid=1)
    tree = [n.model_dump() for n in await svc.tree(user)]
    ids = _collect_ids(tree)

    assert ids == set()
    assert tree[0]["id"] == "0"
    assert tree[0]["children"] == []
