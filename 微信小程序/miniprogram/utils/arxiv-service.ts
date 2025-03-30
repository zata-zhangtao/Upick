/**
 * arXiv API Service
 * 用于获取arXiv论文数据
 */

interface ArxivPaper {
  title: string;
  abstract: string;
  arxiv_id: string;
  arxiv_url: string;
  authors: string[];
  subjects: string;
  comments?: string;
  fetched_at: string;
}

interface ApiResponse {
  success: boolean;
  data?: ArxivPaper[];
  message?: string;
}

// 热门分类
export const POPULAR_CATEGORIES = [
  { code: "cs.AI", name: "Artificial Intelligence" },
  { code: "cs.CL", name: "Computation and Language" },
  { code: "cs.CV", name: "Computer Vision" },
  { code: "cs.LG", name: "Machine Learning" },
  { code: "cs.RO", name: "Robotics" },
  { code: "stat.ML", name: "Statistics - Machine Learning" },
  { code: "physics.comp-ph", name: "Computational Physics" },
  { code: "cs.NE", name: "Neural and Evolutionary Computing" },
  { code: "cs.CY", name: "Computers and Society" },
  { code: "cs.HC", name: "Human-Computer Interaction" }
];

// 获取最新论文 (模拟数据)
export function getLatestPapers(limit: number = 10): Promise<ArxivPaper[]> {
  return new Promise((resolve) => {
    // 实际应用中，这里会从后端API获取数据
    // 此处使用模拟数据
    setTimeout(() => {
      resolve(generateSamplePapers(limit));
    }, 500);
  });
}

// 通过分类获取论文
export function getPapersByCategory(category: string, limit: number = 10): Promise<ArxivPaper[]> {
  return new Promise((resolve) => {
    // 实际应用中，这里会从后端API获取数据
    // 此处使用模拟数据
    setTimeout(() => {
      resolve(generateSamplePapers(limit, category));
    }, 500);
  });
}

// 搜索论文
export function searchPapers(
  searchTerm: string, 
  category?: string, 
  subject?: string, 
  limit: number = 20
): Promise<ArxivPaper[]> {
  return new Promise((resolve) => {
    // 实际应用中，这里会从后端API获取数据
    // 此处使用模拟数据
    const papers = generateSamplePapers(limit, category);
    
    // 简单的过滤逻辑
    if (searchTerm) {
      const filteredPapers = papers.filter(paper => 
        paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        paper.abstract.toLowerCase().includes(searchTerm.toLowerCase()) ||
        paper.authors.some(author => author.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      resolve(filteredPapers);
    } else {
      resolve(papers);
    }
  });
}

// 生成示例论文数据
function generateSamplePapers(count: number = 10, category?: string): ArxivPaper[] {
  const papers: ArxivPaper[] = [];
  const topics = [
    "Deep Learning", "Reinforcement Learning", "Computer Vision", 
    "Natural Language Processing", "Graph Neural Networks",
    "Transformer Models", "GANs", "Diffusion Models"
  ];
  
  for (let i = 0; i < count; i++) {
    const id = Math.floor(Math.random() * 10000000);
    const topic = topics[Math.floor(Math.random() * topics.length)];
    const catCode = category || "cs.AI";
    
    papers.push({
      title: `${topic}: A Novel Approach for Solving Complex Problems ${i+1}`,
      abstract: `We present a new method for ${topic.toLowerCase()} that achieves state-of-the-art results on benchmark datasets. Our approach combines the strengths of multiple existing methods while addressing their limitations. Experimental results show significant improvements over baseline methods.`,
      arxiv_id: `${(new Date()).getFullYear()}.${id}`,
      arxiv_url: `https://arxiv.org/abs/${(new Date()).getFullYear()}.${id}`,
      authors: ["Author One", "Author Two", "Author Three", "Author Four"],
      subjects: category || "Computer Science (cs.AI); Machine Learning (cs.LG)",
      comments: "Accepted at Conference 202X",
      fetched_at: new Date().toISOString().split('T')[0]
    });
  }
  
  return papers;
}

// 获取统计数据
export function getStats(): Promise<{paperCount: number; categoryCount: number; latestUpdate: string}> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        paperCount: 1234,
        categoryCount: 42,
        latestUpdate: new Date().toISOString().split('T')[0]
      });
    }, 300);
  });
} 