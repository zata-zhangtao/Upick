import { getLatestPapers, getStats } from '../../../utils/arxiv-service';

// 导入或定义 ArxivPaper 类型
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

Page({
  data: {
    papers: [] as ArxivPaper[],
    stats: {
      paperCount: 0,
      categoryCount: 0,
      latestUpdate: ''
    },
    loading: true
  },

  onLoad() {
    this.loadData();
  },
  
  onPullDownRefresh() {
    this.loadData();
    wx.stopPullDownRefresh();
  },
  
  async loadData() {
    try {
      this.setData({ loading: true });
      
      // 获取统计数据
      const stats = await getStats();
      
      // 获取最新论文
      const papers = await getLatestPapers(6);
      
      this.setData({
        stats,
        papers,
        loading: false
      });
    } catch (error) {
      console.error('加载数据失败', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
      this.setData({ loading: false });
    }
  },
  
  // 快速抓取特定分类论文
  async fetchCategoryPapers(e: WechatMiniprogram.TouchEvent) {
    const category = e.currentTarget.dataset.category;
    
    wx.navigateTo({
      url: `/pages/arxiv/papers/papers?category=${category}`
    });
  },
  
  // 导航到不同页面
  navigateTo(e: WechatMiniprogram.TouchEvent) {
    const page = e.currentTarget.dataset.page;
    wx.navigateTo({
      url: `/pages/arxiv/${page}/${page}`
    });
  }
}); 