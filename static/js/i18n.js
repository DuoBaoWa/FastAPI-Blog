// 语言资源文件
const translations = {
    'zh': {
        // 导航栏
        'nav_home': '首页',
        'nav_blog': '博客',
        'nav_login': '登录',
        'nav_admin': '管理',
        'nav_logout': '登出',
        
        // 页脚
        'footer_description': '一个现代化的博客平台，基于FastAPI和Markdown构建',
        'footer_copyright': '© 2025 FastAPI Blog. 保留所有权利。',
        
        // 博客列表页
        'no_posts': '没有找到文章。',
        'error_loading_posts': '加载文章出错。请稍后再试。',
        'read_more': '阅读更多',
        'posted_on': '发布于',
        
        // 博客详情页
        'loading_post': '加载文章中...',
        'loading_content': '加载内容中...',
        'post_not_found': '文章未找到。',
        'error_loading_post': '加载文章出错。请稍后再试。',
        'back_to_posts': '返回文章列表',
        'edit_post': '编辑文章',
        
        // 语言切换
        'switch_language': '切换语言',
        'language_zh': '中文',
        'language_en': '英文'
    },
    'en': {
        // Navigation
        'nav_home': 'Home',
        'nav_blog': 'Blog',
        'nav_login': 'Login',
        'nav_admin': 'Admin',
        'nav_logout': 'Logout',
        
        // Footer
        'footer_description': 'A modern blog platform built with FastAPI and Markdown',
        'footer_copyright': '© 2025 FastAPI Blog. All rights reserved.',
        
        // Blog list page
        'no_posts': 'No posts found.',
        'error_loading_posts': 'Error loading posts. Please try again later.',
        'read_more': 'Read More',
        'posted_on': 'Posted on',
        
        // Blog detail page
        'loading_post': 'Loading post...',
        'loading_content': 'Loading content...',
        'post_not_found': 'Post not found.',
        'error_loading_post': 'Error loading post. Please try again later.',
        'back_to_posts': 'Back to Posts',
        'edit_post': 'Edit Post',
        
        // Language switch
        'switch_language': 'Switch Language',
        'language_zh': 'Chinese',
        'language_en': 'English'
    }
};

// 默认语言
let currentLanguage = localStorage.getItem('blog_language') || 'zh';

// 获取翻译文本
function t(key) {
    const translation = translations[currentLanguage][key];
    return translation || key;
}

// 切换语言
function switchLanguage(lang) {
    if (lang && (lang === 'zh' || lang === 'en')) {
        currentLanguage = lang;
        localStorage.setItem('blog_language', lang);
        updatePageText();
    }
}

// 获取当前语言
function getCurrentLanguage() {
    return currentLanguage;
}

// 更新页面上的所有文本
function updatePageText() {
    // 更新导航栏
    const navLinks = document.querySelectorAll('[data-i18n]');
    navLinks.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (key) {
            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = t(key);
            } else {
                element.textContent = t(key);
            }
        }
    });
    
    // 触发自定义事件，通知其他可能需要更新的组件
    document.dispatchEvent(new CustomEvent('languageChanged', {
        detail: { language: currentLanguage }
    }));
}

// 导出函数
window.i18n = {
    t,
    switchLanguage,
    getCurrentLanguage,
    updatePageText
};