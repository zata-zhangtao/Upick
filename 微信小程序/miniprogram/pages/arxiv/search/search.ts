import { searchPapers } from '../../../utils/arxiv-service';

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
    loading: false,
    searchTerm: '',
    subject: 'All Subjects',
    subjects: ['All Subjects', 'Computer Science', 'Physics', 'Mathematics', 'Other'],
    hasSearched: false
  },

  onLoad(options: any) {
    if (options.searchTerm) {
      this.setData({ 
        searchTerm: options.searchTerm
      }, () => {
        this.handleSearch();
      });
    }
    
    if (options.subject) {
      const subject = options.subject;
      if (this.data.subjects.includes(subject)) {
        this.setData({ subject });
      }
    }
  },
  
  // 输入搜索词
  onSearchInput(e: any) {
    this.setData({
      searchTerm: e.detail.value
    });
  },
  
  // 处理搜索
  async handleSearch() {
    const { searchTerm, subject } = this.data;
    
    if (!searchTerm.trim()) {
      wx.showToast({
        title: '请输入搜索内容',
        icon: 'none'
      });
      return;
    }
    
    this.setData({ 
      loading: true,
      hasSearched: true
    });
    
    try {
      const papers = await searchPapers(
        searchTerm,
        undefined,
        subject !== 'All Subjects' ? subject : undefined
      );
      
      this.setData({
        papers,
        loading: false
      });
    } catch (error) {
      console.error('搜索失败', error);
      wx.showToast({
        title: '搜索失败',
        icon: 'error'
      });
      this.setData({ loading: false });
    }
  },
  
  // 处理主题选择
  onSubjectChange(e: any) {
    this.setData({
      subject: this.data.subjects[e.detail.value]
    });
  },
  
  // 清空搜索
  clearSearch() {
    this.setData({
      searchTerm: '',
      papers: [],
      hasSearched: false
    });
  },
  
  // 返回
  navigateBack() {
    wx.navigateBack();
  }
}); 