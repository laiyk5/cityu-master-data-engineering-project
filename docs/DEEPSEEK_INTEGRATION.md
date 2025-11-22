# DeepSeek API 集成说明

## 概述

项目已成功集成 DeepSeek API，用于以下功能：
- **摘要生成**：使用 LLM 生成高质量的新闻主题摘要
- **实体提取**：使用 LLM 识别人物、组织、地点和日期等关键实体

## 配置

### 1. API 密钥配置

在 `.env` 文件中添加 DeepSeek API 密钥：

```env
DEEPSEEK_API_KEY=sk-05058683eb5341deae91bf502be6f957
```

### 2. 配置文件设置

在 `config.json` 中配置 DeepSeek 作为 LLM 提供商：

```json
{
  "summarization": {
    "llm_provider": "deepseek",
    "model": "deepseek-chat",
    "max_tokens": 1000,
    "temperature": 0.7,
    "base_url": "https://api.deepseek.com"
  },
  "entity_extraction": {
    "spacy_model": "en_core_web_sm",
    "min_entity_frequency": 2,
    "use_llm": true
  }
}
```

### 配置参数说明

- **llm_provider**: LLM 提供商（支持 `deepseek`、`openai`、`anthropic`）
- **model**: 使用的模型名称（DeepSeek 使用 `deepseek-chat`）
- **max_tokens**: 最大生成 token 数
- **temperature**: 生成温度（0-1，越高越随机）
- **base_url**: API 端点 URL
- **use_llm**: 是否启用 LLM 进行实体提取（默认 true）

## 功能特性

### 1. 智能摘要生成

DeepSeek API 可以：
- 分析多篇新闻文章
- 提取主要事件和发展
- 识别关键人物和组织
- 生成客观中立的主题摘要
- 支持中英文内容

**示例输出**（来自实际运行）：
```
美国高级军事代表团在乌克兰进行和平谈判，引发国际社会对俄乌冲突解决方案的关注。
根据美国军方声明，由陆军部长丹·德里斯科尔率领的五角大楼代表团已抵达乌克兰，
旨在就"结束战争"事宜展开磋商...
```

### 2. LLM 实体提取

启用 `use_llm: true` 后，系统将使用 DeepSeek 进行实体提取：

**提取类别**：
- **people**: 人物（政治家、企业家、专家等）
- **organizations**: 组织机构（公司、政府机构、国际组织等）
- **locations**: 地点（国家、城市、地区等）
- **dates**: 日期（重要时间点）

**优势**：
- 比传统 NER（命名实体识别）更准确
- 理解上下文语义
- 支持多语言
- 可识别复杂实体关系

## 使用方法

### 运行完整管道

```bash
python main.py
```

管道会自动：
1. 爬取新闻数据
2. 清洗和去重
3. 使用 DeepSeek 提取实体
4. 使用 DeepSeek 生成摘要
5. 生成时间线
6. 生成 HTML 报告

### 单独测试摘要生成

```python
from summarizer import Summarizer

summarizer = Summarizer()
articles = [
    {
        'title': '新闻标题',
        'content': '新闻内容...'
    }
]

summary = summarizer.generate_summary(articles)
print(summary)
```

### 单独测试实体提取

```python
from entity_extractor import EntityExtractor

extractor = EntityExtractor()
entities_data = extractor.extract_and_rank(articles)
print(entities_data)
```

## 回退机制

系统具有完善的回退机制：

1. **摘要生成回退**：
   - DeepSeek API 失败 → 使用备用简单拼接方法

2. **实体提取回退**：
   - DeepSeek API 失败 → spaCy NER
   - spaCy 不可用 → 基于正则表达式的简单提取

3. **多级容错**：
   - API 密钥缺失
   - 网络连接问题
   - API 限额超出
   - JSON 解析错误

## 性能优化

### API 调用优化

- 文本长度限制：实体提取时截取前 2000 字符
- 批量处理：每 10 篇文章记录一次进度
- 温度设置：实体提取使用较低温度（0.3）保证准确性

### 成本控制

- 使用 `max_tokens` 限制生成长度
- 实体提取仅处理文章开头部分
- 启用缓存避免重复调用

## 故障排查

### 问题 1: API 调用失败

```
ERROR - DeepSeek API调用失败: ...
```

**解决方案**：
1. 检查 `.env` 中的 API 密钥是否正确
2. 确认网络连接正常
3. 验证 API 账户余额

### 问题 2: JSON 解析错误

```
ERROR - LLM实体提取失败: Expecting value: line 1 column 1
```

**解决方案**：
- 系统已实现自动处理 markdown 代码块
- 会自动回退到 spaCy 方法
- 检查日志查看原始返回内容

### 问题 3: Unicode 编码警告

```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**说明**：
- 这是 Windows 控制台显示问题
- 不影响程序正常运行
- 数据文件正确保存为 UTF-8

## API 费用估算

基于 DeepSeek 定价：
- 输入：约 0.14 元/百万 tokens
- 输出：约 0.28 元/百万 tokens

**典型使用场景**：
- 处理 100 篇新闻文章
- 每篇约 500 词
- 预计成本：< 0.5 元

## 切换到其他 LLM 提供商

### 切换到 OpenAI

```json
{
  "summarization": {
    "llm_provider": "openai",
    "model": "gpt-3.5-turbo"
  }
}
```

在 `.env` 中添加：
```env
OPENAI_API_KEY=your-openai-api-key
```

### 切换到 Anthropic Claude

```json
{
  "summarization": {
    "llm_provider": "anthropic",
    "model": "claude-3-sonnet-20240229"
  }
}
```

在 `.env` 中添加：
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## 最佳实践

1. **API 密钥安全**
   - 不要提交 `.env` 到版本控制
   - 定期轮换 API 密钥
   - 使用环境变量管理

2. **性能优化**
   - 限制每次处理的文章数量
   - 使用合适的 max_tokens 值
   - 监控 API 使用量

3. **质量保证**
   - 定期检查生成的摘要质量
   - 验证实体提取准确性
   - 调整 temperature 参数优化输出

## 技术支持

如有问题，请：
1. 查看日志文件了解详细错误信息
2. 参考 README.md 和其他文档
3. 检查 DeepSeek API 官方文档
4. 使用备用回退机制确保系统正常运行

## 更新日志

- **2025-11-20**: 初始集成 DeepSeek API
  - 添加摘要生成支持
  - 添加实体提取支持
  - 实现多级回退机制
  - 完成测试和验证
