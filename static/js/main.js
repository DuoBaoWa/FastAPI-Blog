document.addEventListener('DOMContentLoaded', function() {
    // 检查是否登录
    const token = localStorage.getItem('token');
    if (token) {
        fetchUserInfo(token);
    } else {
        document.getElementById('login-link').style.display = 'block';
        document.getElementById('admin-link').style.display = 'none';
        document.getElementById('logout-link').style.display = 'none';
    }

    // 登出逻辑
    document.getElementById('logout-link').addEventListener('click', function(e) {
        e.preventDefault();
        localStorage.removeItem('token');
        window.location.href = '/';
    });
    
    // 监听语言变化事件，更新动态内容
    document.addEventListener('languageChanged', function(e) {
        // 如果在博客列表页面
        if (document.getElementById('posts-container')) {
            loadPosts();
        }
        
        // 如果在博客详情页面
        const postTitle = document.getElementById('post-title');
        if (postTitle && postTitle.dataset.postId) {
            loadPost(postTitle.dataset.postId);
        }
    });
});

async function fetchUserInfo(token) {
    try {
        const response = await fetch('/api/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.status === 401) {
            // Token invalid or expired
            localStorage.removeItem('token');
            document.getElementById('login-link').style.display = 'block';
            document.getElementById('admin-link').style.display = 'none';
            document.getElementById('logout-link').style.display = 'none';
            return;
        }
        
        const userData = await response.json();
        
        document.getElementById('login-link').style.display = 'none';
        document.getElementById('logout-link').style.display = 'block';
        
        // 如果是管理员，显示管理员链接
        if (userData.is_admin) {
            document.getElementById('admin-link').style.display = 'block';
        } else {
            document.getElementById('admin-link').style.display = 'none';
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
    }
}

// 用于博客页面加载文章
async function loadPosts() {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        const response = await fetch('/api/posts', {
            headers: headers
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch posts');
        }
        
        const posts = await response.json();
        const postsContainer = document.getElementById('posts-container');
        
        if (posts.length === 0) {
            postsContainer.innerHTML = `<p>${window.i18n.t('no_posts')}</p>`;
            return;
        }
        
        let html = '';
        posts.forEach(post => {
            html += `
                <article class="post-card">
                    <h2><a href="/blog/${post.id}">${post.title}</a></h2>
                    <p class="post-meta">
                        ${window.i18n.t('posted_on')} ${new Date(post.created_at).toLocaleDateString()}
                    </p>
                    <div class="post-excerpt">
                        ${post.content.substring(0, 150)}...
                    </div>
                    <a href="/blog/${post.id}" class="read-more">${window.i18n.t('read_more')}</a>
                </article>
            `;
        });
        
        postsContainer.innerHTML = html;
    } catch (error) {
        console.error('Error loading posts:', error);
        document.getElementById('posts-container').innerHTML = 
            `<p>${window.i18n.t('error_loading_posts')}</p>`;
    }
}

// 用于单篇博客文章页面
async function loadPost(postId) {
    try {
        const token = localStorage.getItem('token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        const response = await fetch(`/api/posts/${postId}`, {
            headers: headers
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                document.getElementById('post-container').innerHTML = 
                    `<p>${window.i18n.t('post_not_found')}</p>`;
            } else {
                throw new Error('Failed to fetch post');
            }
            return;
        }
        
        const post = await response.json();
        const postTitle = document.getElementById('post-title');
        postTitle.textContent = post.title;
        postTitle.dataset.postId = postId; // 存储文章ID用于语言切换时重新加载
        
        document.getElementById('post-date').textContent = 
            new Date(post.created_at).toLocaleDateString();
        document.getElementById('post-content').innerHTML = post.content;
        
        // 如果是管理员，显示编辑按钮
        const userData = token ? await getUserData(token) : null;
        if (userData && userData.is_admin) {
            const editBtn = document.getElementById('edit-post-btn');
            editBtn.style.display = 'inline-block';
            editBtn.href = `/admin/posts/${postId}/edit`;
            editBtn.textContent = window.i18n.t('edit_post');
        }
        
        // 更新返回按钮文本
        const backBtn = document.querySelector('.btn-back');
        if (backBtn) {
            backBtn.innerHTML = `<span class="btn-icon">←</span> ${window.i18n.t('back_to_posts')}`;
        }
    } catch (error) {
        console.error('Error loading post:', error);
        document.getElementById('post-container').innerHTML = 
            `<p>${window.i18n.t('error_loading_post')}</p>`;
    }
}

async function getUserData(token) {
    try {
        const response = await fetch('/api/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) return null;
        return await response.json();
    } catch (error) {
        console.error('Error getting user data:', error);
        return null;
    }
}