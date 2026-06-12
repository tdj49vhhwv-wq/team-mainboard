"""
Pydantic v2 模型 — Week 2 两类基础事实记录

1. SubscriptionFlow  — 认缴流量: 谁在什么时候认购了多少、多少钱、什么价格
2. EquitySnapshot   — 股权结构存量: 某个时点的股东结构是什么

重要规则:
  - PDF 只披露出资额 → 只填出资额, 持股数空着
  - PDF 只披露持股数 → 只填持股数, 出资额空着
  - 不要为了填满表格去倒推
"""

from typing import Optional, List
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


# ============================================================
# 枚举
# ============================================================

class RecordType(str, Enum):
    SUBSCRIPTION_FLOW = "subscription_flow"
    EQUITY_SNAPSHOT = "equity_snapshot"


class Currency(str, Enum):
    CNY = "CNY"
    USD = "USD"
    HKD = "HKD"


# ============================================================
# 1. 认缴流量 — SubscriptionFlow
# ============================================================

class SubscriptionFlow(BaseModel):
    """
    认缴流量: 回答"谁在什么时候认购了多少、多少钱、什么价格"

    每行 = 一个认购方在一次增资/股权变动中的认购记录。
    一个融资事件如果有 N 个认购方, 就产生 N 行 subscription_flow。
    """
    record_type: RecordType = Field(
        default=RecordType.SUBSCRIPTION_FLOW,
        description="记录类型标识"
    )
    company_name: str = Field(
        ...,
        min_length=1,
        description="公司全称"
    )
    stock_code: str = Field(
        ...,
        min_length=1,
        pattern=r'^\d{6}$',
        description="股票代码（6位）"
    )

    # 定位
    source_page: str = Field(
        ...,
        min_length=1,
        description="PDF 页码或 MD 文件行号范围"
    )

    # 认购信息
    subscription_date: str = Field(
        ...,
        min_length=7,
        description="增资/认购日期（YYYY-MM-DD 或 YYYY-MM）"
    )
    subscriber_name: str = Field(
        ...,
        min_length=1,
        description="认购方名称"
    )

    # 数量/金额/价格（可为空，不强行倒推）
    shares_subscribed: Optional[float] = Field(
        None,
        ge=0,
        description="认购数量（万股）。PDF 未披露则留空"
    )
    amount_subscribed: Optional[float] = Field(
        None,
        ge=0,
        description="认购金额（万元人民币）。PDF 未披露则留空"
    )
    price_per_share: Optional[float] = Field(
        None,
        ge=0,
        description="认购价格（元/股 或 元/注册资本）。PDF 未披露则留空"
    )

    # 证据
    evidence_text: str = Field(
        ...,
        min_length=20,
        description="原文逐字摘录（必须是 PDF 原文片段，不可人工概括）"
    )
    notes: Optional[str] = Field(
        None,
        description="备注（人工概括放这里）"
    )

    @field_validator("subscription_date")
    @classmethod
    def check_date(cls, v: str) -> str:
        import re
        if not re.match(r'^\d{4}-\d{2}(-\d{2})?$', v):
            raise ValueError(f"日期格式错误: {v}，应为 YYYY-MM-DD 或 YYYY-MM")
        return v

    @field_validator("evidence_text")
    @classmethod
    def check_not_summary(cls, v: str) -> str:
        summary_starts = ["招股书显示", "招股书披露", "根据招股书", "据招股书"]
        for kw in summary_starts:
            if v.strip().startswith(kw):
                raise ValueError(f"evidence_text 疑似概括性语言，应为原文逐字摘录")
        return v


# ============================================================
# 2. 股权结构存量 — EquitySnapshot
# ============================================================

class EquitySnapshot(BaseModel):
    """
    股权结构存量: 回答"某个时点股东结构是什么"

    每行 = 一个股东在一个快照时点的持仓。
    必须包含 t0（报告期初或可识别的最早股权结构）。
    """
    record_type: RecordType = Field(
        default=RecordType.EQUITY_SNAPSHOT,
        description="记录类型标识"
    )
    company_name: str = Field(
        ...,
        min_length=1,
        description="公司全称"
    )
    stock_code: str = Field(
        ...,
        min_length=1,
        pattern=r'^\d{6}$',
        description="股票代码（6位）"
    )

    # 定位
    source_page: str = Field(
        ...,
        min_length=1,
        description="PDF 页码或 MD 文件行号范围"
    )

    # 快照信息
    snapshot_date: str = Field(
        ...,
        min_length=7,
        description="时点（YYYY-MM-DD 或 YYYY-MM）"
    )
    snapshot_type: str = Field(
        ...,
        min_length=1,
        description="股权结构口径（如: 报告期初 / 有限公司设立时 / 股改后 / XX轮增资后 / IPO前）"
    )

    # 总量（同快照所有行一致）
    total_shares: Optional[float] = Field(
        None,
        ge=0,
        description="总股本（万股）。PDF 未披露则留空"
    )
    total_capital: Optional[float] = Field(
        None,
        ge=0,
        description="总出资额 / 注册资本（万元）。PDF 未披露则留空"
    )

    # 股东持仓
    shareholder_name: str = Field(
        ...,
        min_length=1,
        description="股东名称"
    )
    shares_held: Optional[float] = Field(
        None,
        ge=0,
        description="持股数（万股）。PDF 未按股数披露则留空"
    )
    capital_contribution: Optional[float] = Field(
        None,
        ge=0,
        description="出资额（万元注册资本）。PDF 未按出资额披露则留空"
    )
    shareholding_ratio: Optional[str] = Field(
        None,
        description="持股比例（如 25.00%）"
    )

    # 证据
    evidence_text: str = Field(
        ...,
        min_length=20,
        description="原文逐字摘录"
    )
    notes: Optional[str] = Field(
        None,
        description="备注"
    )

    @field_validator("snapshot_date")
    @classmethod
    def check_date(cls, v: str) -> str:
        import re
        if not re.match(r'^\d{4}-\d{2}(-\d{2})?$', v):
            raise ValueError(f"日期格式错误: {v}")
        return v

    @field_validator("evidence_text")
    @classmethod
    def check_not_summary(cls, v: str) -> str:
        summary_starts = ["招股书显示", "招股书披露", "根据招股书", "据招股书"]
        for kw in summary_starts:
            if v.strip().startswith(kw):
                raise ValueError(f"evidence_text 疑似概括性语言，应为原文逐字摘录")
        return v


# 联合类型: SubscriptionFlow | EquitySnapshot（在 validate 中分别处理）
