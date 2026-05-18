# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.models.template import VisualizationTemplate, VisualizationTemplateCategory  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.template_repo import (  # pyright: ignore[reportImplicitRelativeImport]
    TemplateCategoryMapRepository,
    TemplateCategoryRepository,
    TemplateRepository,
)
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.template import (  # pyright: ignore[reportImplicitRelativeImport]
    BatchDeleteRequest,
    BatchUpdateRequest,
    FindCategoriesByTemplateIdsRequest,
    FindCategoriesRequest,
    NameCheckRequest,
    TemplateFindRequest,
    TemplateListBodyRequest,
    TemplateSaveRequest,
    TemplateUpdateRequest,
)
from app.services.template_service import (  # pyright: ignore[reportImplicitRelativeImport]
    TemplateService,
    _build_tree,
    _cat_to_dict,
    _tpl_to_dict,
)


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _service(session: AsyncSession) -> TemplateService:
    return TemplateService(session)


def _unit_service() -> TemplateService:
    async def _delete(*_args: object, **_kwargs: object) -> None:
        return None

    async def _commit() -> None:
        return None

    session = cast(AsyncSession, cast(object, SimpleNamespace(delete=_delete, commit=_commit)))
    return TemplateService(session)


def _template_payload(stamp: int, *, name: str, dv_type: str = "dashboard", template_type: str = "self") -> dict[str, object]:
    return {
        "id": str(_stamp()),
        "name": f"{name}-{stamp}",
        "pid": "0",
        "level": 0,
        "dv_type": dv_type,
        "node_type": "panel",
        "create_by": "7",
        "create_time": _timestamp_ms(),
        "snapshot": "snap",
        "template_type": template_type,
        "template_style": {"theme": "light"},
        "template_data": {"widgets": 1},
        "dynamic_data": {"dataset": "demo"},
    }


def _category_payload(
    stamp: int,
    *,
    name: str,
    pid: str = "0",
    level: int = 0,
    dv_type: str = "dashboard",
    template_type: str = "self",
) -> dict[str, object]:
    return {
        "id": str(_stamp()),
        "name": f"{name}-{stamp}",
        "pid": pid,
        "level": level,
        "dv_type": dv_type,
        "node_type": "folder",
        "create_by": "7",
        "create_time": _timestamp_ms(),
        "snapshot": None,
        "template_type": template_type,
    }


async def _cleanup_templates(
    session: AsyncSession,
    *,
    template_ids: list[str],
    category_ids: list[str],
) -> None:
    map_repo = TemplateCategoryMapRepository(session)
    tpl_repo = TemplateRepository(session)
    cat_repo = TemplateCategoryRepository(session)
    for template_id in template_ids:
        try:
            await map_repo.delete_by_template_id(template_id)
        except Exception:
            pass
        entity = await tpl_repo.get_by_id(template_id)
        if entity is not None:
            try:
                await tpl_repo.delete(entity)
            except Exception:
                pass
    for category_id in category_ids:
        entity = await cat_repo.get_by_id(category_id)
        if entity is not None:
            try:
                await cat_repo.delete(entity)
            except Exception:
                pass


class FakeStoreRepo:
    def __init__(self, existing: object | None = None, stores: list[object] | None = None) -> None:
        self.existing = existing
        self.stores = stores or []
        self.created: list[dict[str, object]] = []
        self.deleted: list[tuple[int, int, int]] = []

    async def get_by_resource(self, resource_id: int, uid: int, resource_type: int) -> object | None:
        _ = (resource_id, uid, resource_type)
        return self.existing

    async def delete_by_resource(self, resource_id: int, uid: int, resource_type: int) -> None:
        self.deleted.append((resource_id, uid, resource_type))

    async def create(self, payload: dict[str, object]) -> object:
        self.created.append(payload)
        return SimpleNamespace(**payload)

    async def query_by_user(self, uid: int) -> list[object]:
        _ = uid
        return self.stores


class FakeTemplateRepo:
    def __init__(self, templates: list[object]) -> None:
        self.templates = templates

    async def list_all(self) -> list[object]:
        return self.templates


class FakeMapRepo:
    def __init__(self, maps_by_category: dict[str, list[object]] | None = None) -> None:
        self.maps_by_category = maps_by_category or {}

    async def list_by_category_id(self, category_id: str) -> list[object]:
        return self.maps_by_category.get(category_id, [])


def test_build_tree_and_serializers_cover_nested_nodes() -> None:
    root = VisualizationTemplateCategory(**_category_payload(_stamp(), name="root"))
    child = VisualizationTemplateCategory(**_category_payload(_stamp(), name="child", pid=root.id, level=1))
    leaf = VisualizationTemplate(**_template_payload(_stamp(), name="leaf"))

    tree = _build_tree([root, child])

    assert len(tree) == 1
    assert tree[0].id == root.id
    assert tree[0].children[0].id == child.id
    assert _cat_to_dict(root)["name"] == root.name
    assert _tpl_to_dict(leaf)["templateType"] == "self"


@pytest.mark.asyncio
async def test_name_check_honors_create_and_update_modes() -> None:
    service = _unit_service()
    cast(Any, service).template_repo = FakeTemplateRepo(
        [
            SimpleNamespace(id="tpl-1", name="Alpha"),
            SimpleNamespace(id="tpl-2", name="Beta"),
        ]
    )

    assert await service.name_check(NameCheckRequest(name="Alpha", opt_type=None)) == "exist_all"
    assert await service.name_check(NameCheckRequest(name="Alpha", id="tpl-1", opt_type="update")) == "none"
    assert await service.name_check(NameCheckRequest(name="Beta", id="tpl-1", opt_type="update")) == "exist_all"
    assert await service.category_template_name_check(
        cast(Any, SimpleNamespace(name="Alpha", categories=["cat-1"]))
    ) == "none"


@pytest.mark.asyncio
async def test_check_category_template_and_favorite_methods() -> None:
    service = _unit_service()
    cast(Any, service).category_map_repo = FakeMapRepo({"cat-1": [SimpleNamespace(template_id="tpl-1")]})
    add_repo = FakeStoreRepo()
    remove_repo = FakeStoreRepo(existing=SimpleNamespace(id=1))

    cast(Any, service).store_repo = add_repo
    favorited = await service.toggle_favorite(101, 7, 2)
    assert favorited == {"favorited": True}
    assert add_repo.created[0]["resource_id"] == 101

    cast(Any, service).store_repo = remove_repo
    unfavorited = await service.toggle_favorite(101, 7, 2)
    assert unfavorited == {"favorited": False}
    assert remove_repo.deleted == [(101, 7, 2)]

    cast(Any, service).store_repo = FakeStoreRepo(
        stores=[SimpleNamespace(id=1, resource_id=9, uid=7, resource_type=0, time=123)]
    )
    assert await service.check_category_template("cat-1") is True
    assert await service.check_category_template("missing") is False
    assert await service.list_favorites(7) == [
        {"id": 1, "resourceId": 9, "uid": 7, "resourceType": 0, "time": 123}
    ]


@pytest.mark.asyncio
async def test_tree_attaches_only_existing_templates() -> None:
    service = _unit_service()
    category = VisualizationTemplateCategory(**_category_payload(_stamp(), name="root"))
    template = VisualizationTemplate(**_template_payload(_stamp(), name="kept"))
    cast(Any, service).category_map_repo = FakeMapRepo(
        {category.id: [SimpleNamespace(template_id=template.id), SimpleNamespace(template_id="missing")]}
    )

    async def _list_all() -> list[VisualizationTemplateCategory]:
        return [category]

    async def _get_by_id(template_id: str) -> VisualizationTemplate | None:
        return template if template_id == template.id else None

    cast(Any, service).category_repo = SimpleNamespace(list_all=_list_all)
    cast(Any, service).template_repo = SimpleNamespace(get_by_id=_get_by_id)

    tree = await service.tree()
    assert tree[0]["children"][0]["id"] == template.id
    assert len(tree[0]["children"]) == 1


class TestTemplateServiceIntegration:
    pytestmark = [
        pytest.mark.asyncio,
        pytest.mark.skipif(
            os.getenv("DE_E2E") != "1",
            reason="Requires PostgreSQL (set DE_E2E=1)",
        ),
    ]

    async def test_save_find_update_list_and_delete_template(self, db_session: AsyncSession) -> None:
        service = _service(db_session)
        template_ids: list[str] = []
        try:
            created = await service.save(
                TemplateSaveRequest(
                    name=f"service-template-{_stamp()}",
                    node_type="panel",
                    dv_type="dashboard",
                    template_type="self",
                    template_style={"font": 12},
                    template_data={"items": [1]},
                    dynamic_data={"refresh": True},
                ),
                _user(),
            )
            template_ids.append(created["id"])

            fetched = await service.find_one(created["id"])
            by_body = await service.find_by_body(
                TemplateFindRequest(id=created["id"], template_id=None)
            )
            all_names = await service.name_list()
            listed = await service.list_templates("service-template")
            filtered = await service.template_list(
                TemplateListBodyRequest(
                    category_id=None,
                    dv_type="dashboard",
                    template_type="self",
                    keyword="service-template",
                )
            )
            updated = await service.update(
                TemplateUpdateRequest(
                    id=created["id"],
                    name="updated-template-name",
                    snapshot="snap-2",
                    template_style={"font": 18},
                    template_data={"items": [2]},
                    dynamic_data={"refresh": False},
                )
            )

            assert fetched is not None
            assert fetched["id"] == created["id"]
            assert by_body[0]["id"] == created["id"]
            assert any(item["id"] == created["id"] for item in all_names)
            assert any(item["id"] == created["id"] for item in listed)
            assert filtered[0]["templateType"] == "self"
            assert updated["name"] == "updated-template-name"
            assert await service.find_by_body(
                TemplateFindRequest(id=None, template_id=created["id"])
            )

            await service.delete(created["id"])
            template_ids.clear()
            assert await service.find_one(created["id"]) is None
            assert await service.find_by_body(
                TemplateFindRequest(id=created["id"], template_id=None)
            ) == []
        finally:
            await _cleanup_templates(db_session, template_ids=template_ids, category_ids=[])

    async def test_categories_tree_form_find_and_delete_category(self, db_session: AsyncSession) -> None:
        service = _service(db_session)
        cat_repo = TemplateCategoryRepository(db_session)
        map_repo = TemplateCategoryMapRepository(db_session)
        tpl_repo = TemplateRepository(db_session)
        template_ids: list[str] = []
        category_ids: list[str] = []
        try:
            root = await cat_repo.create(_category_payload(_stamp(), name="cat-root", template_type="market"))
            child = await cat_repo.create(
                _category_payload(_stamp(), name="cat-child", pid=root.id, level=1, template_type="market")
            )
            template = await tpl_repo.create(_template_payload(_stamp(), name="mapped", template_type="market"))
            await map_repo.create({"id": str(_stamp()), "template_id": template.id, "category_id": child.id})
            category_ids.extend([root.id, child.id])
            template_ids.append(template.id)

            categories = await service.categories()
            filtered = await service.find_categories(
                FindCategoriesRequest(dv_type="dashboard", template_type="market")
            )
            form = await service.category_form(child.id)
            tree = await service.tree()

            root_payload = next(item for item in categories if item["id"] == root.id)
            filtered_root = next(item for item in filtered if item["id"] == root.id)
            tree_root = next(item for item in tree if item["id"] == root.id)
            assert root_payload["children"][0]["id"] == child.id
            assert filtered_root["children"][0]["id"] == child.id
            assert form["category"]["id"] == child.id
            assert form["templates"][0]["id"] == template.id
            assert tree_root["children"][0]["id"] == child.id

            assert await service.check_category_template(child.id) is True
            assert child.id in await service.find_categories_by_template_ids(
                FindCategoriesByTemplateIdsRequest(template_ids=[template.id])
            )

            assert await service.delete_category(child.id) == "success"
            category_ids.remove(child.id)
            assert await service.check_category_template(child.id) is False
            with pytest.raises(HTTPException):
                await service.category_form(child.id)
        finally:
            await _cleanup_templates(db_session, template_ids=template_ids, category_ids=category_ids)

    async def test_batch_update_batch_delete_and_category_scoped_delete(self, db_session: AsyncSession) -> None:
        service = _service(db_session)
        cat_repo = TemplateCategoryRepository(db_session)
        tpl_repo = TemplateRepository(db_session)
        map_repo = TemplateCategoryMapRepository(db_session)
        template_ids: list[str] = []
        category_ids: list[str] = []
        try:
            cat_one = await cat_repo.create(_category_payload(_stamp(), name="batch-one"))
            cat_two = await cat_repo.create(_category_payload(_stamp(), name="batch-two"))
            category_ids.extend([cat_one.id, cat_two.id])
            first = await tpl_repo.create(_template_payload(_stamp(), name="batch-first"))
            second = await tpl_repo.create(_template_payload(_stamp(), name="batch-second"))
            third = await tpl_repo.create(_template_payload(_stamp(), name="batch-third"))
            template_ids.extend([first.id, second.id, third.id])

            await service.batch_update(
                BatchUpdateRequest(template_ids=[first.id, second.id], categories=[cat_one.id, cat_two.id])
            )
            cat_one_templates = await service.template_list(
                TemplateListBodyRequest(
                    category_id=cat_one.id,
                    dv_type=None,
                    template_type=None,
                    keyword=None,
                )
            )
            assert {item["id"] for item in cat_one_templates} == {first.id, second.id}

            await map_repo.create({"id": str(_stamp()), "template_id": third.id, "category_id": cat_two.id})
            await service.delete(first.id, cat_one.id)
            assert await service.find_one(first.id) is not None

            await service.batch_delete(
                BatchDeleteRequest(template_ids=[first.id, second.id], categories=[cat_two.id])
            )
            assert await service.find_one(first.id) is None
            assert await service.find_one(second.id) is not None

            await service.batch_delete(BatchDeleteRequest(template_ids=[second.id], categories=[cat_one.id]))
            assert await service.find_one(second.id) is None
            template_ids = [third.id]

            await service.batch_delete(BatchDeleteRequest(template_ids=[third.id], categories=None))
            template_ids.clear()
            assert await service.find_one(third.id) is None
        finally:
            await _cleanup_templates(db_session, template_ids=template_ids, category_ids=category_ids)

    async def test_missing_template_and_category_raise_not_found(self, db_session: AsyncSession) -> None:
        service = _service(db_session)

        with pytest.raises(HTTPException) as update_exc:
            await service.update(
                TemplateUpdateRequest(
                    id="missing",
                    name="x",
                    snapshot=None,
                    template_style=None,
                    template_data=None,
                    dynamic_data=None,
                )
            )
        with pytest.raises(HTTPException) as delete_exc:
            await service.delete("missing")
        with pytest.raises(HTTPException) as category_exc:
            await service.delete_category("missing")

        assert update_exc.value.status_code == 404
        assert delete_exc.value.status_code == 404
        assert category_exc.value.status_code == 404
