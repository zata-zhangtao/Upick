import { searchPapers, getPapersByCategory } from '../../../utils/arxiv-service';

// 定义 ArxivPaper 类型
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
    loading: true,
    searchTerm: '',
    category: '',
    subject: 'All Subjects',
    subjects: ['All Subjects', 'Computer Science', 'Physics', 'Mathematics', 'Other'],
    limit: 20,
    currentPage: 1,
    hasMore: true
  },

  onLoad(options: any) {
    if (options.category) {
      this.setData({ category: options.category });
    }
    
    if (options.subject) {
      this.setData({ subject: options.subject });
    }
    
    if (options.searchTerm) {
      this.setData({ searchTerm: options.searchTerm });
    }
    
    this.loadPapers();
  },
  
  onPullDownRefresh() {
    this.resetAndLoad();
    wx.stopPullDownRefresh();
  },
  
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMorePapers();
    }
  },
  
  // 重置分页并加载
  resetAndLoad() {
    this.setData({
      papers: [],
      currentPage: 1,
      hasMore: true
    }, () => {
      this.loadPapers();
    });
  },
  
  // 加载论文
  async loadPapers() {
    try {
      this.setData({ loading: true });
      
      let papers;
      if (this.data.category) {
        // 按分类获取
        papers = await getPapersByCategory(this.data.category, this.data.limit);
      } else {
        // 搜索获取
        papers = await searchPapers(
          this.data.searchTerm,
          this.data.category,
          this.data.subject !== 'All Subjects' ? this.data.subject : undefined,
          this.data.limit
        );
      }
      
      this.setData({
        papers,
        loading: false,
        hasMore: papers.length === this.data.limit
      });
    } catch (error) {
      console.error('加载论文失败', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
      this.setData({ loading: false });
    }
  },
  
  // 加载更多论文
  async loadMorePapers() {
    if (this.data.loading || !this.data.hasMore) {
      return;
    }
    
    try {
      this.setData({ 
        loading: true,
        currentPage: this.data.currentPage + 1
      });
      
      let morePapers;
      if (this.data.category) {
        morePapers = await getPapersByCategory(this.data.category, this.data.limit);
      } else {
        morePapers = await searchPapers(
          this.data.searchTerm,
          this.data.category,
          this.data.subject !== 'All Subjects' ? this.data.subject : undefined,
          this.data.limit
        );
      }
      
      // 合并数据
      if (morePapers.length > 0) {
        this.setData({
          papers: [...this.data.papers, ...morePapers],
          loading: false,
          hasMore: morePapers.length === this.data.limit
        });
      } else {
        this.setData({
          loading: false,
          hasMore: false
        });
      }
    } catch (error) {
      console.error('加载更多论文失败', error);
      this.setData({ 
        loading: false,
        currentPage: this.data.currentPage - 1
      });
    }
  },
  
  // 处理搜索
  handleSearch() {
    this.resetAndLoad();
  },
  
  // 处理输入变化
  onSearchInput(e: any) {
    this.setData({
      searchTerm: e.detail.value
    });
  },
  
  // 处理主题变化
  onSubjectChange(e: any) {
    this.setData({
      subject: this.data.subjects[e.detail.value]
    }, () => {
      this.resetAndLoad();
    });
  },
  
  // 返回首页
  navigateBack() {
    wx.navigateBack();
  }
}); 