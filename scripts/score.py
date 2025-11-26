from abc import ABC, abstractmethod
from atss.ai import OpenAIClient, test_openai_client
from typing import Any
from atss import logger

class CritizeResult:
    """评价结果类"""
    
    def __init__(self, score: float, comments: str):
        self.score = score
        self.comments = comments

class Criticizer(ABC):
    """General Criticizer class to evaluate modules"""

    @abstractmethod
    def criticize_module(self, inputs: dict[str, Any]) -> CritizeResult:
        """Evaluate the given module with inputs and return a CritizeResult"""
        pass


import tenacity
import json
class LLMCriticizer(Criticizer):

    @tenacity.retry(
        wait=tenacity.wait_fixed(1),
        stop=tenacity.stop_after_attempt(5),
        reraise=False,
        retry=tenacity.retry_if_exception_type(json.JSONDecodeError)
    )
    def criticize_module(self, inputs) -> CritizeResult:
        """Evaluate module using LLM"""
        module_name = inputs["module_name"]
        module_input = inputs["module_input"]
        module_output = inputs["module_output"]
        requirement = inputs["requirement"]
        
        # Construct prompt for LLM
        prompt = f"""
        You are an expert evaluator. Please evaluate the following module output based on the requirement.
        
        Module Name: {module_name}
        Requirement: {requirement}
        Module Input: {module_input}
        Module Output: {module_output}
        
        Provide a score between 0 and 100 and detailed comments, and put a summarized version in the comments.
        
        Return a JSON object as follows:
        {{
          "score": <score>,
          "comments": "<summarized comments>"
        }}
        """
        
        with OpenAIClient() as client:  # client is acturally using DeepSeek API
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a professional module evaluator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
            )
        
        # Parse response to extract score and comments
        # (Assuming the response format is consistent)

        result_text = response.choices[0].message.content.strip()
        logger.info(f"评价器响应: {result_text}")

        if not result_text.startswith("{"):
            # Try to extract JSON part
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            result_text = result_text[json_start:json_end]

        import json
        result_json = json.loads(result_text)
        score = result_json.get("score", 0)
        comments = result_json.get("comments", "")


        # validate score
        if not (0 <= score <= 100):
            score = 0
            comments += " | Invalid score received, set to 0."
        
        return CritizeResult(score=score, comments=comments)

class ModuleCriticizer:
    def __init__(self):
        self.criticizer = LLMCriticizer()
    
    def criticize(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> CritizeResult:
        module_input = self._prepare_inputs(module_name, module_input, module_output, requirement)
        module_output = self._prepare_outputs(module_name, module_input, module_output, requirement)

        inputs = {
            "module_name": module_name,
            "module_input": module_input,
            "module_output": module_output,
            "requirement": requirement,
        }

        logger.info(f"评价器输入: {inputs}")
        return self.criticizer.criticize_module(inputs)

    @abstractmethod
    def _prepare_inputs(self, module_name: str, module_input: dict | list , module_output: dict | list, requirement: str) -> dict:
        """Prepare inputs for criticizer if needed"""
        pass

    @abstractmethod
    def _prepare_outputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        """Prepare outputs for criticizer if needed"""
        pass



MODULES_DEFINITIONS = {
    "data_fetcher": {
        "requirements": "Fetch relevant news articles based on the given topic from various sources. Consider comprehensiveness first.",
        "input_file": "",
        "output_file": "raw_articles.json",
    },
    "article_cleaner": {
        "requirements": "Clean the raw articles by removing HTML tags, special characters, and irrelevant content.",
        "input_file": "raw_articles.json",
        "output_file": "cleaned_articles.json",
    },
    "deduplicator": {
        "requirements": "Remove duplicate articles based on title and content similarity.",
        "input_file": "raw_articles.json",
        "output_file": "deduplicated_articles.json",
    },
    "entity_extractor": {
        "requirements": "Extract key entities such as people, organizations, and locations from the articles.",
        "input_file": "deduplicated_articles.json",
        "output_file": "entities.json",
    },
    "summarizer": {
        "requirements": "Generate a concise summary of the topic based on the articles.",
        "input_file": "deduplicated_articles.json",
        "output_file": "summary.json",
    },
    "timeline_generator": {
        "requirements": "Create a timeline of events from the articles.",
        "input_file": "summary.json",
        "output_file": "timeline.json",
    },
}

class DataFetcherCriticizer(ModuleCriticizer):
    def _prepare_inputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For data fetcher, we can limit the input to just the topic
        return {"topic": module_input.get("topic", "")}

    def _prepare_outputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For data fetcher, we can limit the output to just the titles of fetched articles
        return {"article_titles": [article.get("title", "") for article in module_output]}


class ArticleCleanerCriticizer(ModuleCriticizer):
    def _prepare_inputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For article cleaner, we can limit the input to just the raw content of articles
        # Assuming module_input is a list of articles
        return {"raw_contents_first_500_characters": [article.get("content", "")[:500] for article in module_input]}
    
    def _prepare_outputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For article cleaner, we can limit the output to just the cleaned content of articles
        return {"cleaned_contents_first_500_characters": [article.get("content", "")[:500] for article in module_output]}

class DeduplicatorCriticizer(ModuleCriticizer):
    def _prepare_inputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For deduplicator, we can limit the input to just the titles of articles
        return {"article_titles": [article.get("title", "") for article in module_input]}
    
    def _prepare_outputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For deduplicator, we can limit the output to just the titles of deduplicated articles
        return {"deduplicated_article_titles": [article.get("title", "") for article in module_output]}


class entityExtractorCriticizer(ModuleCriticizer):
    def _prepare_inputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For entity extractor, we can limit the input to just the titles and contents of articles
        return {"article_titles_and_contents_first_500_characters": [
            {
                "title": article.get("title", ""),
                "content": article.get("content", "")[:500]
            } for article in module_input
        ]}
    
    def _prepare_outputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For entity extractor, we can limit the output to just the extracted entities
        return {"extracted_entities": module_output}
    

class SummarizerCriticizer(ModuleCriticizer):
    def _prepare_inputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For summarizer, we can limit the input to just the titles of articles
        return {"article_titles": [article.get("title", "") for article in module_input]}
    
    def _prepare_outputs(self, module_name: str, module_input: dict | list, module_output: dict | list, requirement: str) -> dict:
        # For summarizer, we can limit the output to just the generated summary
        return {"summary": module_output.get("summary", "")}
    


def main():
    # test openai client
    with OpenAIClient() as client:
        test_openai_client()

    # get user input to gain scoring inputs
    scoring_dataset_dir = input("请输入评分数据集目录路径: ").strip()
    scoring_dataset_dir = scoring_dataset_dir if scoring_dataset_dir else "/Users/laiyk/Dev/Master/CS5481-DataEngineering/Project/cityu-master-data-engineering-project/examples/NvidiaH20GPU"
    topic = input("请输入评分使用的主题（默认使用评分目录名称）: ").strip()
    topic = topic if topic else scoring_dataset_dir.split("/")[-1]
    logger.info(f"使用目录 {scoring_dataset_dir}")
    logger.info(f"使用主题: {topic}")
    import os
    import json

    # checklist: set of all input/output files in modules definitions
    checklist = set(
        [MODULES_DEFINITIONS[module]["input_file"] for module in MODULES_DEFINITIONS] +
        [MODULES_DEFINITIONS[module]["output_file"] for module in MODULES_DEFINITIONS]
    )

    # check if all files exist
    for file in checklist:
        if file and not os.path.exists(os.path.join(scoring_dataset_dir, file)):
            print(f"缺少必要的文件: {file}，请检查评分数据集目录。")
            return

    # read all files into memory
    data_files = {}
    for file in checklist:
        if file:
            with open(os.path.join(scoring_dataset_dir, file), 'r', encoding='utf-8') as f:
                data_files[file] = json.load(f)
    
    
    # initialize criticizer
    criticizers = {
        "data_fetcher": DataFetcherCriticizer(),
        "article_cleaner": ArticleCleanerCriticizer(),
        "deduplicator": DeduplicatorCriticizer(),
        "entity_extractor": entityExtractorCriticizer(),
        "summarizer": SummarizerCriticizer(),
    }

    scoring_result = {}

    for module_name, definition in MODULES_DEFINITIONS.items():
        print(f"\n=== 评估模块: {module_name} ===")
        criticizer = criticizers.get(module_name)
        if not criticizer:
            print(f"⚠️  未找到对应的评价器，跳过模块 {module_name} 的评价。")
            continue
        
        module_input = {}
        if definition["input_file"]:
            module_input = data_files.get(definition["input_file"], {})

        if module_name == "data_fetcher":
            module_input["topic"] = topic
        
        module_output = {}
        if definition["output_file"]:
            module_output = data_files.get(definition["output_file"], {})
        
        requirement = definition["requirements"]
        
        result = criticizer.criticize(
            module_name=module_name,
            module_input=module_input,
            module_output=module_output,
            requirement=requirement
        )
        scoring_result[module_name] = result

        print(f"评分: {result.score}/100")
        print(f"评论: {result.comments}")

    # report the scoring results
    print("\n=== 模块评分汇总 ===")
    total_score = 0
    for module_name, result in scoring_result.items():
        print(f"{module_name}: {result.score}/100")
        total_score += result.score
    average_score = total_score / len(scoring_result) if scoring_result else 0
    print(f"\n平均评分: {average_score}/100")

    # generate a markdown table for the results
    print("\n=== 模块评分表格 ===")
    print("topic: ", topic)
    print("| modulename | score (0-100) | comment |")
    print("| --- | --- | --- |")

    for module_name, result in scoring_result.items():
        comment = result.comments.replace("\n", " ").replace("|", "/")
        print(f"| {module_name} | {result.score} | {comment} |")

    # export the result as json file
    output_path = os.path.join(scoring_dataset_dir, "scoring_result.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(
            {
                module_name: {
                    "score": result.score,
                    "comments": result.comments
                } for module_name, result in scoring_result.items()
            },
            f,
            ensure_ascii=False,
            indent=2
        )
    print(f"\n✓ 评分结果已保存到 {output_path}")

if __name__ == "__main__":
    main()