# DeepSeek API 快速开始指南

## 30秒快速配置

### 步骤 1: 获取 DeepSeek API 密钥

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号并登录
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 API Key（格式：`sk-xxxxxxxx...`）

### 步骤 2: 配置项目

编辑 `.env` 文件（如果不存在，从 `.env.example` 复制）：

```env
DEEPSEEK_API_KEY=sk-05058683eb5341deae91bf502be6f957
```

**完成！** 现在可以直接运行项目了。

### 步骤 3: 运行项目

```bash
python main.py
```

或使用主题搜索：

```bash
python topic_search.py
```

## 验证配置

运行测试脚本确认一切正常：

```bash
python test_deepseek.py
```

## 费用说明

DeepSeek 定价（截至 2024年）：
- **输入**: ~¥0.14 / 百万 tokens
- **输出**: ~¥0.28 / 百万 tokens

### 典型使用成本

| 场景 | 文章数 | 预计费用 |
|------|--------|----------|
| 小型测试 | 10篇 | < ¥0.05 |
| 中型项目 | 100篇 | < ¥0.50 |
| 大型项目 | 1000篇 | < ¥5.00 |

**注意**: 实际费用取决于文章长度和生成的摘要长度。

## 高级配置

### 调整模型参数

编辑 `config.json`：

```json
{
  "summarization": {
    "llm_provider": "deepseek",
    "model": "deepseek-chat",
    "max_tokens": 1000,        // 增加可获得更长摘要
    "temperature": 0.7,        // 降低使输出更确定
    "base_url": "https://api.deepseek.com"
  }
}
```

### 参数说明

- **max_tokens**: 
  - 500-1000: 简短摘要（推荐）
  - 1000-2000: 详细摘要
  - 2000+: 非常详细的分析

- **temperature**:
  - 0.3: 非常确定性（用于事实提取）
  - 0.7: 平衡创造性和准确性（推荐）
  - 1.0: 更有创造性

### 启用/禁用 LLM 实体提取

在 `config.json` 中：

```json
{
  "entity_extraction": {
    "use_llm": true,  // 设为 false 使用 spaCy/正则表达式
    "min_entity_frequency": 2
  }
}
```

## 切换到其他 LLM

### 使用 OpenAI

```json
{
  "summarization": {
    "llm_provider": "openai",
    "model": "gpt-3.5-turbo"
  }
}
```

`.env`:
```env
OPENAI_API_KEY=sk-...
```

### 使用 Anthropic Claude

```json
{
  "summarization": {
    "llm_provider": "anthropic",
    "model": "claude-3-sonnet-20240229"
  }
}
```

`.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

## 故障排查

### 问题: API 调用失败

**错误信息**:
```
ERROR - DeepSeek API调用失败: ...
```

**解决方案**:
1. 检查 API Key 是否正确
2. 确认账户有余额
3. 检查网络连接
4. 查看 DeepSeek 服务状态

### 问题: 返回内容为空

**原因**: 可能是 JSON 解析失败

**解决方案**:
- 系统会自动回退到 spaCy 或简单提取
- 检查日志查看详细错误
- 尝试调整 temperature 参数

### 问题: Unicode 编码错误

**错误信息**:
```
UnicodeEncodeError: 'gbk' codec can't encode...
```

**解决方案**:
- 这是 Windows 控制台显示问题
- **不影响功能**，数据文件正常
- 可以忽略这些警告

## 性能优化建议

### 1. 批量处理

处理大量文章时：
- 设置合理的 `max_articles_per_source`
- 分批运行而不是一次性处理所有

### 2. 缓存结果

- 生成的摘要保存在 `data/summary.json`
- 提取的实体保存在 `data/entities.json`
- 可以重用这些结果而不需要重新调用 API

### 3. 限制文本长度

系统已自动：
- 摘要生成：每篇文章取前 500 字符
- 实体提取：每篇文章取前 2000 字符

## 监控 API 使用

### 查看使用情况

登录 DeepSeek 控制台查看：
- API 调用次数
- Token 消耗量
- 当前余额

### 设置使用限额

在代码中可以添加：
```python
# 限制每天最多处理的文章数
MAX_DAILY_ARTICLES = 1000
```

## 最佳实践

1. **开发阶段**: 使用小数据集测试
2. **生产环境**: 启用错误日志和监控
3. **成本控制**: 设置合理的 token 限制
4. **质量保证**: 定期检查生成的摘要质量

## 示例代码

### 直接调用 DeepSeek API

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### 使用项目封装的类

```python
from summarizer import Summarizer

# 初始化
summarizer = Summarizer()

# 生成摘要
articles = [{"title": "...", "content": "..."}]
summary = summarizer.generate_summary(articles)
print(summary)
```

## 获取帮助

- 📖 完整文档: `DEEPSEEK_INTEGRATION.md`
- 🧪 运行测试: `python test_deepseek.py`
- 📋 项目文档: `README.md`
- 🗄️ 数据库指南: `DATABASE_README.md`

## 下一步

1. ✅ 配置完成 → 运行 `python test_deepseek.py`
2. ✅ 测试通过 → 运行 `python main.py`
3. ✅ 查看结果 → 打开 `output/topic_summary.html`

**开始使用吧！** 🚀
