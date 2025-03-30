Component({
  properties: {
    paper: {
      type: Object,
      value: {}
    }
  },
  data: {
    showFullAbstract: false
  },
  methods: {
    toggleAbstract() {
      this.setData({
        showFullAbstract: !this.data.showFullAbstract
      });
    },
    
    openPaperLink() {
      const url = this.properties.paper.arxiv_url;
      wx.setClipboardData({
        data: url,
        success: () => {
          wx.showToast({
            title: '链接已复制',
            icon: 'success'
          });
        }
      });
    },
    
    formatAuthors(authors: string[]) {
      if (!authors || authors.length === 0) {
        return "Unknown Authors";
      }
      
      if (authors.length > 3) {
        return `${authors[0]}, ${authors[1]}, ${authors[2]}, et al.`;
      }
      
      return authors.join(", ");
    }
  }
}); 