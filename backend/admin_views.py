"""sqladmin ModelView definitions for the admin panel at /admin."""

from sqladmin import ModelView

from models.account import Account
from models.usage_record import UsageRecord
from models.quota_snapshot import QuotaSnapshot
from models.alert_rule import AlertRule
from models.gemini_quota_config import GeminiQuotaConfig


class AccountAdmin(ModelView, model=Account):
    name = "Account"
    name_plural = "Accounts"
    icon = "fa-solid fa-user"
    column_list = [
        Account.id,
        Account.label,
        Account.email,
        Account.gmail_slot,
        Account.source,
        Account.is_active,
    ]
    column_searchable_list = [Account.label, Account.email]
    column_filters = [Account.source, Account.gmail_slot, Account.is_active]
    column_sortable_list = [Account.label, Account.source]
    form_include_pk = True


class UsageRecordAdmin(ModelView, model=UsageRecord):
    name = "Usage Record"
    name_plural = "Usage Records"
    icon = "fa-solid fa-chart-bar"
    column_list = [
        UsageRecord.timestamp,
        UsageRecord.account_id,
        UsageRecord.source,
        UsageRecord.model_label,
        UsageRecord.input_tokens,
        UsageRecord.output_tokens,
        UsageRecord.cost_usd,
        UsageRecord.request_count,
    ]
    column_sortable_list = [
        UsageRecord.timestamp,
        UsageRecord.input_tokens,
        UsageRecord.output_tokens,
    ]
    column_filters = [
        UsageRecord.source,
        UsageRecord.account_id,
        UsageRecord.model_id,
    ]
    column_default_sort = (UsageRecord.timestamp, True)
    can_create = False
    can_delete = True
    can_export = True
    page_size = 50


class QuotaSnapshotAdmin(ModelView, model=QuotaSnapshot):
    name = "Quota Snapshot"
    name_plural = "Quota Snapshots"
    icon = "fa-solid fa-gauge"
    column_list = [
        QuotaSnapshot.snapshot_at,
        QuotaSnapshot.account_id,
        QuotaSnapshot.source,
        QuotaSnapshot.model_label,
        QuotaSnapshot.quota_remaining_pct,
        QuotaSnapshot.reset_at,
        QuotaSnapshot.is_exhausted,
        QuotaSnapshot.reset_cadence,
    ]
    column_sortable_list = [QuotaSnapshot.snapshot_at]
    column_filters = [QuotaSnapshot.source, QuotaSnapshot.account_id]
    column_default_sort = (QuotaSnapshot.snapshot_at, True)
    can_create = False
    can_export = True
    page_size = 50


class AlertRuleAdmin(ModelView, model=AlertRule):
    name = "Alert Rule"
    name_plural = "Alert Rules"
    icon = "fa-solid fa-bell"
    column_list = [
        AlertRule.label,
        AlertRule.account_id,
        AlertRule.source,
        AlertRule.threshold_pct,
        AlertRule.channel,
        AlertRule.last_fired_at,
        AlertRule.is_active,
    ]
    column_filters = [AlertRule.source, AlertRule.channel, AlertRule.is_active]
    can_export = True


class GeminiQuotaConfigAdmin(ModelView, model=GeminiQuotaConfig):
    name = "Gemini Quota Config"
    name_plural = "Gemini Quota Configs"
    icon = "fa-solid fa-sliders"
    column_list = [
        GeminiQuotaConfig.model_id,
        GeminiQuotaConfig.model_label,
        GeminiQuotaConfig.rpm,
        GeminiQuotaConfig.tpm,
        GeminiQuotaConfig.rpd,
    ]
    form_include_pk = True
    can_export = True
