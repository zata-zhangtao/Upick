import { POPULAR_CATEGORIES } from '../../../utils/arxiv-service';

interface Category {
  code: string;
  name: string;
}

Page({
  data: {
    categories: [] as Category[],
    searchTerm: ''
  },

  onLoad() {
    this.setData({
      categories: POPULAR_CATEGORIES
    });
  },
  
  // 搜索分类
  onSearchInput(e: any) {
    const searchTerm = e.detail.value.toLowerCase();
    this.setData({ searchTerm });
  },
  
  // 获取过滤后的分类
  getFilteredCategories(): Category[] {
    const { categories, searchTerm } = this.data;
    
    if (!searchTerm) {
      return categories;
    }
    
    return categories.filter(category => 
      category.code.toLowerCase().includes(searchTerm) || 
      category.name.toLowerCase().includes(searchTerm)
    );
  },
  
  // 导航到论文页面
  navigateToPapers(e: WechatMiniprogram.TouchEvent) {
    const category = e.currentTarget.dataset.category;
    wx.navigateTo({
      url: `/pages/arxiv/papers/papers?category=${category}`
    });
  },
  
  // 返回上一页
  navigateBack() {
    wx.navigateBack();
  }
}); 