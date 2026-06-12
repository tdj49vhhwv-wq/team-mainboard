# PEVC 招股说明书融资历史提取 — Week 2

从 8 家公共样本的 IPO 招股说明书中提取融资历史事件和财务三表数据，输出结构化 JSONL。

## 运行方式

```bash
# 1. 生成 JSONL（8 家公司）
python3 scripts/generate_jsonl.py

# 2. Schema + Cross-Check 校验
python3 scripts/validate_jsonl.py

# 3. JSONL → Excel
python3 scripts/jsonl_to_excel.py
```

## 目录结构

```
├── company_list/week2_public_8.csv   # 8 家公共样本清单
├── schemas/extraction_models.py      # Pydantic 字段定义（变量说明见 Field description）
├── scripts/
│   ├── generate_jsonl.py             # JSONL 生成
│   ├── validate_jsonl.py             # Schema 校验 + 数值 Cross-Check
│   └── jsonl_to_excel.py             # JSONL → 三表 Excel
├── outputs/
│   ├── week2_jsonl/                  # 主结果：8 个 .jsonl
│   └── week2_excel/                  # 查看版：8 个 _三表抽取.xlsx
├── logs/
│   ├── schema_validation_log.csv     # 逐记录逐检查项
│   └── cross_check_summary.csv       # 总量核对 + 逐事件核对
├── prompts/llm_prompt.md             # 可执行 LLM Prompt
├── annotations_pdf/                  # PDF 批注截图（待补充）
└── weekly_reports/week2.md           # 周报
```

## 校验结果

- Pydantic Schema: **8/8 PASS**
- Cross-Check (总额 vs 投资人出资之和): **14/14 PASS**
- 5 家手动深度提取: evidence_text 均为原文逐字摘录
- 3 家 review 笔记: 待 PDF 解析后补充原文证据

## 变量定义

全部在 `schemas/extraction_models.py` 的 Pydantic Field 中，包括字段名、类型、必填项、枚举值范围和校验规则。核心模型:
- `FinancingEvent` — 融资事件 (19 字段)
- `FinancialStatementRecord` — 三表数据 (12 字段)
- `Investor` — 投资人明细 (8 字段)
