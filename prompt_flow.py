from fastmcp import FastMCP, Context
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent
from typing import List, Dict, Any
import json

mcp = FastMCP(
    name="PromptFlowServer",
    instructions="""Prompt Flow server providing various prompt templates for different use cases.

Available prompts:
- explain_topic: Generate explanation request prompts
- start_roleplay: Generate roleplay conversation starters  
- generate_report: Generate formatted report templates

Use these prompts to guide LLM interactions and responses.
""",
)

@mcp.prompt
def explain_topic(topic: str) -> str:
    """
    生成解释某个主题的提示模板
    
    Args:
        topic: 需要解释的主题
        
    Returns:
        用于请求解释的提示文本
    """
    return f"请你详细解释一下「{topic}」的概念，包括其定义、原理、应用场景等方面的内容。"

@mcp.prompt
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """Generates a user message requesting code generation."""
    content = f"Write a {language} function that performs the following task: {task_description}"
    return PromptMessage(role="user", content=TextContent(type="text", text=content))

@mcp.prompt
def start_roleplay(character: str) -> List[Dict[str, str]]:
    """
    生成角色扮演对话的开场模板
    
    Args:
        character: 要扮演的角色
        
    Returns:
        包含用户提示和助手确认的多条消息
    """
    return [
        {
            "role": "user",
            "content": f"让我们来进行角色扮演游戏。你现在是{character}，请完全沉浸在这个角色中，用{character}的身份、语气和思维方式来回应我。准备好了吗？"
        },
        {
            "role": "assistant", 
            "content": f"好的！我现在就是{character}。我已经准备好了，让我们开始这场角色扮演吧！你想要我做什么或者想和我聊什么呢？"
        }
    ]

@mcp.prompt()
def generate_report(title: str, data: List[int]) -> str:
    """
    生成格式化报告模板
    
    Args:
        title: 报告标题
        data: 要展示的数据列表
        
    Returns:
        格式化的Markdown报告模板
    """
    data_items = '\n'.join([f"- 项目 {i+1}: {value}" for i, value in enumerate(data)])
    
    template = f"""# {title}

## 数据概览

{data_items}

## 统计分析

- 总数量: {len(data)}
- 最大值: {max(data) if data else 'N/A'}
- 最小值: {min(data) if data else 'N/A'}
- 平均值: {sum(data) / len(data):.2f if data else 'N/A'}

## 结论

请根据以上数据生成相应的分析结论和建议。
"""
    
    return template

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """
    生成代码审查提示模板
    
    Args:
        language: 编程语言
        code: 要审查的代码
        
    Returns:
        代码审查提示模板
    """
    return f"""请对以下{language}代码进行全面的代码审查：

```{language}
{code}
```

请从以下几个方面进行分析：

1. **代码质量**: 可读性、可维护性、代码风格
2. **性能优化**: 是否有性能瓶颈或优化空间
3. **安全性**: 是否存在安全漏洞或风险
4. **最佳实践**: 是否遵循该语言的最佳实践
5. **错误处理**: 异常处理是否完善
6. **改进建议**: 具体的改进建议和重构方案

请提供详细的分析和具体的改进代码示例。
"""

@mcp.prompt()
def learning_plan(topic: str, level: str, duration: str) -> str:
    """
    生成学习计划模板
    
    Args:
        topic: 学习主题
        level: 当前水平 (初级/中级/高级)
        duration: 学习时长
        
    Returns:
        个性化学习计划模板
    """
    return f"""请为我制定一个关于「{topic}」的{duration}学习计划，我目前的水平是{level}。

请按以下结构制定计划：

## 学习目标
- 明确这个学习计划要达到的具体目标

## 前置知识
- 列出需要具备的基础知识

## 学习路径
### 第一阶段：基础概念
- 学习内容
- 推荐资源
- 实践项目

### 第二阶段：深入理解  
- 学习内容
- 推荐资源
- 实践项目

### 第三阶段：实际应用
- 学习内容
- 推荐资源
- 综合项目

## 学习资源推荐
- 书籍
- 在线课程
- 实践平台
- 社区论坛

## 学习检验
- 每个阶段的评估标准
- 推荐的练习题或项目

请提供详细且可执行的学习计划。
"""

if __name__ == "__main__":
    mcp.run()