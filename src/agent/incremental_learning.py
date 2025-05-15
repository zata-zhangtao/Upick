from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from pydantic import BaseModel
from src.log import get_logger
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import pickle

logger = get_logger("agent.incremental_learning")

def tokenize_text(text: str) -> List[str]:
    """
    使用jieba进行中文分词
    Args:
        text: 输入文本
    Returns:
        List[str]: 分词结果列表
    """
    return list(jieba.cut(text))

class LearningExample(BaseModel):
    """学习示例的数据模型"""
    input_text: str
    output_text: str
    feedback_score: float
    timestamp: str
    metadata: Dict = {}

class IncrementalLearner:
    def __init__(self, storage_path: str = "resources/learning_data"):
        """
        初始化增量学习器
        Args:
            storage_path: 学习数据存储路径
        """
        self.storage_path = storage_path
        self.examples: List[LearningExample] = []
        self.vectorizer = TfidfVectorizer(
            tokenizer=tokenize_text,
            max_features=10000
        )
        self.vectors = None
        self._ensure_storage_path()
        self._load_existing_data()
        self._train_model()

    def _ensure_storage_path(self):
        """确保存储路径存在"""
        os.makedirs(self.storage_path, exist_ok=True)

    def _load_existing_data(self):
        """加载现有的学习数据"""
        data_file = os.path.join(self.storage_path, "learning_data.json")
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.examples = [LearningExample(**example) for example in data]
                logger.info(f"成功加载 {len(self.examples)} 条学习数据")
            except Exception as e:
                logger.error(f"加载学习数据失败: {str(e)}")
                self.examples = []

    def _train_model(self):
        """训练文本相似度模型"""
        if not self.examples:
            logger.warning("没有足够的数据来训练模型")
            return

        try:
            # 准备训练数据
            texts = [example.input_text for example in self.examples]
            
            # 训练TF-IDF向量化器
            self.vectors = self.vectorizer.fit_transform(texts)
            
            # 保存模型
            model_path = os.path.join(self.storage_path, "model.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'vectors': self.vectors
                }, f)
            
            logger.info("模型训练完成并保存")
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)} at line {e.__traceback__.tb_lineno}")

    def _load_model(self):
        """加载已训练的模型"""
        model_path = os.path.join(self.storage_path, "model.pkl")
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.vectorizer = model_data['vectorizer']
                    self.vectors = model_data['vectors']
                logger.info("成功加载已训练的模型")
            except Exception as e:
                logger.error(f"加载模型失败: {str(e)}")
                self._train_model()

    def save_example(self, input_text: str, output_text: str, feedback_score: float, metadata: Dict = None):
        """
        保存学习示例
        Args:
            input_text: 输入文本
            output_text: 输出文本
            feedback_score: 反馈分数 (0-1)
            metadata: 额外的元数据
        """
        example = LearningExample(
            input_text=input_text,
            output_text=output_text,
            feedback_score=feedback_score,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        self.examples.append(example)
        self._save_data()
        
        # 重新训练模型
        self._train_model()
        
        logger.info(f"保存新的学习示例，当前共有 {len(self.examples)} 条数据")

    def _save_data(self):
        """保存学习数据到文件"""
        data_file = os.path.join(self.storage_path, "learning_data.json")
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump([example.dict() for example in self.examples], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存学习数据失败: {str(e)}")

    def get_similar_examples(self, input_text: str, top_k: int = 3) -> List[LearningExample]:
        """
        获取与输入文本相似的历史示例
        Args:
            input_text: 输入文本
            top_k: 返回的示例数量
        Returns:
            List[LearningExample]: 相似的历史示例列表
        """
        if not self.examples:
            return []

        try:
            # 确保模型已加载
            if self.vectors is None:
                self._load_model()
                if self.vectors is None:
                    return self.examples[-top_k:]

            # 转换输入文本为向量
            input_vector = self.vectorizer.transform([input_text])
            
            # 计算相似度
            similarities = cosine_similarity(input_vector, self.vectors).flatten()
            
            # 获取最相似的示例索引
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # 返回相似度最高的示例
            similar_examples = [self.examples[i] for i in top_indices]
            
            # 记录相似度分数
            for i, example in enumerate(similar_examples):
                example.metadata['similarity_score'] = float(similarities[top_indices[i]])
            
            logger.debug(f"找到 {len(similar_examples)} 个相似示例，最高相似度: {similarities[top_indices[0]]:.4f}")
            return similar_examples

        except Exception as e:
            logger.error(f"获取相似示例失败: {str(e)}")
            return self.examples[-top_k:]

    def get_learning_statistics(self) -> Dict:
        """
        获取学习统计信息
        Returns:
            Dict: 包含统计信息的字典
        """
        if not self.examples:
            return {
                "total_examples": 0,
                "average_feedback": 0,
                "latest_update": None,
                "model_status": "未训练"
            }

        return {
            "total_examples": len(self.examples),
            "average_feedback": sum(e.feedback_score for e in self.examples) / len(self.examples),
            "latest_update": max(e.timestamp for e in self.examples),
            "model_status": "已训练" if self.vectors is not None else "未训练",
            "vocabulary_size": len(self.vectorizer.vocabulary_) if self.vectorizer is not None else 0
        }

def main():
    """测试增量学习功能"""
    # 初始化学习器
    learner = IncrementalLearner()
    
    # 准备测试数据
    test_examples = [
        {
            "input_text": "Flower Labs发布混合计算平台Flower Intelligence，获2360万美元融资，支持本地与云端混合运行AI模型，提升速度与隐私保护。",
            "output_text": "Flower Labs推出混合计算平台，获2360万美元融资，支持本地/云端混合部署AI模型，兼顾速度与隐私",
            "feedback_score": 0.9
        },
        {
            "input_text": "潞晨科技开源视频生成模型Open-Sora 2.0，成本降至20万美元，参数110亿，性能对标OpenAI Sora，挑战行业标杆HunyuanVideo和Step-Video",
            "output_text": "潞晨科技开源Open-Sora 2.0视频模型，成本20万美元，110亿参数，性能接近Sora，挑战HunyuanVideo和Step-Video",
            "feedback_score": 0.85
        },
        {
            "input_text": "美国埃隆大学调查显示，55%的美国成年人都曾使用过AI大语言模型，其中ChatGPT最受欢迎，使用率达72%，谷歌的Gemini位居第二，使用率为50%。",
            "output_text": "埃隆大学调查：55%美国成年人使用过AI大模型，ChatGPT最受欢迎(72%)，Gemini次之(50%)",
            "feedback_score": 0.95
        }
    ]
    
    # 保存测试数据
    print("保存测试数据...")
    for example in test_examples:
        learner.save_example(
            input_text=example["input_text"],
            output_text=example["output_text"],
            feedback_score=example["feedback_score"],
            metadata={"source": "test_data"}
        )
    
    # 查看学习统计
    stats = learner.get_learning_statistics()
    print("\n学习统计信息:")
    print(f"总示例数: {stats['total_examples']}")
    print(f"平均反馈分数: {stats['average_feedback']:.2f}")
    print(f"模型状态: {stats['model_status']}")
    print(f"词汇表大小: {stats['vocabulary_size']}")
    
    # 测试相似度查询
    test_queries = [
        "Flower Labs推出新的AI计算平台",
        "潞晨科技发布视频模型",
        "美国大学AI使用调查"
    ]
    
    print("\n测试相似度查询:")
    for query in test_queries:
        print(f"\n查询: {query}")
        similar_examples = learner.get_similar_examples(query, top_k=2)
        for i, example in enumerate(similar_examples, 1):
            print(f"\n相似示例 {i}:")
            print(f"相似度: {example.metadata['similarity_score']:.4f}")
            print(f"输入: {example.input_text}")
            print(f"输出: {example.output_text}")
            print(f"反馈分数: {example.feedback_score}")

if __name__ == "__main__":
    main() 