from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class FilingConfigCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    target_datasource_id: int | None = Field(
        None,
        validation_alias=AliasChoices("targetDatasourceId", "target_datasource_id"),
        serialization_alias="targetDatasourceId",
    )
    target_table: str | None = Field(
        None,
        validation_alias=AliasChoices("targetTable", "target_table"),
        serialization_alias="targetTable",
    )
    form_schema: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("formSchema", "form_schema"),
        serialization_alias="formSchema",
    )
    field_mapping: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("fieldMapping", "field_mapping"),
        serialization_alias="fieldMapping",
    )
    idempotency_window_seconds: int = Field(
        300,
        validation_alias=AliasChoices("idempotencyWindowSeconds", "idempotency_window_seconds"),
        serialization_alias="idempotencyWindowSeconds",
    )
    oid: int | None = None


class FilingConfigUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    target_datasource_id: int | None = Field(
        None,
        validation_alias=AliasChoices("targetDatasourceId", "target_datasource_id"),
        serialization_alias="targetDatasourceId",
    )
    target_table: str | None = Field(
        None,
        validation_alias=AliasChoices("targetTable", "target_table"),
        serialization_alias="targetTable",
    )
    form_schema: dict[str, Any] | None = Field(
        None,
        validation_alias=AliasChoices("formSchema", "form_schema"),
        serialization_alias="formSchema",
    )
    field_mapping: dict[str, Any] | None = Field(
        None,
        validation_alias=AliasChoices("fieldMapping", "field_mapping"),
        serialization_alias="fieldMapping",
    )
    idempotency_window_seconds: int | None = Field(
        None,
        validation_alias=AliasChoices("idempotencyWindowSeconds", "idempotency_window_seconds"),
        serialization_alias="idempotencyWindowSeconds",
    )


class FilingSubmitRequest(BaseModel):
    model_config = ConfigDict(extra="allow")


class FilingConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    status: str
    target_datasource_id: int | None = Field(
        None,
        validation_alias=AliasChoices("targetDatasourceId", "target_datasource_id"),
        serialization_alias="targetDatasourceId",
    )
    target_table: str | None = Field(
        None,
        validation_alias=AliasChoices("targetTable", "target_table"),
        serialization_alias="targetTable",
    )
    form_schema: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("formSchema", "form_schema"),
        serialization_alias="formSchema",
    )
    field_mapping: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("fieldMapping", "field_mapping"),
        serialization_alias="fieldMapping",
    )
    idempotency_window_seconds: int = Field(
        300,
        validation_alias=AliasChoices("idempotencyWindowSeconds", "idempotency_window_seconds"),
        serialization_alias="idempotencyWindowSeconds",
    )
    oid: int | None = None
    creator_uid: int | None = Field(
        None,
        validation_alias=AliasChoices("creatorUid", "creator_uid"),
        serialization_alias="creatorUid",
    )
    create_time: datetime | str | None = Field(
        None,
        validation_alias=AliasChoices("createTime", "create_time"),
        serialization_alias="createTime",
    )
    update_time: datetime | str | None = Field(
        None,
        validation_alias=AliasChoices("updateTime", "update_time"),
        serialization_alias="updateTime",
    )


class FilingSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    filing_id: int = Field(
        ..., validation_alias=AliasChoices("filingId", "filing_id"), serialization_alias="filingId"
    )
    payload_hash: str | None = Field(
        None,
        validation_alias=AliasChoices("payloadHash", "payload_hash"),
        serialization_alias="payloadHash",
    )
    payload: dict[str, Any] | None = None
    status: str
    error_message: str | None = Field(
        None,
        validation_alias=AliasChoices("errorMessage", "error_message"),
        serialization_alias="errorMessage",
    )
    submitter_uid: int | None = Field(
        None,
        validation_alias=AliasChoices("submitterUid", "submitter_uid"),
        serialization_alias="submitterUid",
    )
    retry_count: int = Field(
        0,
        validation_alias=AliasChoices("retryCount", "retry_count"),
        serialization_alias="retryCount",
    )
    create_time: datetime | str | None = Field(
        None,
        validation_alias=AliasChoices("createTime", "create_time"),
        serialization_alias="createTime",
    )
    update_time: datetime | str | None = Field(
        None,
        validation_alias=AliasChoices("updateTime", "update_time"),
        serialization_alias="updateTime",
    )


class FilingAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    filing_id: int = Field(
        ..., validation_alias=AliasChoices("filingId", "filing_id"), serialization_alias="filingId"
    )
    submission_id: int | None = Field(
        None,
        validation_alias=AliasChoices("submissionId", "submission_id"),
        serialization_alias="submissionId",
    )
    action: str
    actor_uid: int | None = Field(
        None,
        validation_alias=AliasChoices("actorUid", "actor_uid"),
        serialization_alias="actorUid",
    )
    details: dict[str, Any] | None = None
    outcome: str
    error_code: str | None = Field(
        None,
        validation_alias=AliasChoices("errorCode", "error_code"),
        serialization_alias="errorCode",
    )
    create_time: datetime | str | None = Field(
        None,
        validation_alias=AliasChoices("createTime", "create_time"),
        serialization_alias="createTime",
    )
