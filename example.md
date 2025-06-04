## 已关联到以下数据

表名：**company_bidding_info**，描述：**企业中标信息表**

|  字段名 | 字段描述      |
|--------|----------|
| unified_social_credit_code   | 统一社会信用代码        |
| company_name   | 企业名称       |
| winning_amount   | 中标金额(万元)        |
| winning_date   | 中标日期       |

## SQL语法

\`\`\`sql
SELECT YEAR(winning_date) AS year, 
COUNT(DISTINCT unified_social_credit_code) 
AS company_count FROM company_bidding_info 
GROUP BY YEAR(winning_date) ORDER BY year;
\`\`\`

## 数据展示

问题：统计各年份中标企业有多少家？

|  年份  | 数量      |
|--------|----------|
| 2023   | 5        |
| 2024   | 30       |
| 2025   | 6        |

\`\`\`echarts
{
  "title": { "text": "" },
  "xAxis": { "type": "category", "data": ["2023", "2024", "2025"] },
  "yAxis": { "type": "value" },
  "series": [{ "type": "line", "data": [5, 30, 6], "smooth": true }]
}
\`\`\`

## 结果评价

从统计结果来看，各年份的中标企业数量呈现明显的波动趋势。2024年的中标企业数量显著高于其他年份，达到30家，是2023年（5家）的6倍，也远超2025年（6家）的5倍。这种差异可能反映了2024年市场需求的激增、招标项目的集中释放，或政策环境的变化。相比之下，2023年和2025年的数据较为接近，但整体偏低，可能需要结合行业背景（如经济周期、政策调整等）进一步分析原因。若数据覆盖完整年度，2025年数量较低也可能与统计时间范围不足（如仅包含年初数据）有关。建议补充更多背景信息以验证趋势的合理性。
