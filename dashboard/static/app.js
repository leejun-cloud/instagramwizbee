let currentPosts = [];
let currentEditingDay = null;

const postGrid = document.getElementById('postGrid');
const autoPublishToggle = document.getElementById('autoPublishToggle');

// Modal Elements
const editModal = document.getElementById('editModal');
const modalDayNumber = document.getElementById('modalDayNumber');
const editHook = document.getElementById('editHook');
const editCaption = document.getElementById('editCaption');
const editHashtags = document.getElementById('editHashtags');

// Initialize
async function init() {
    await loadSettings();
    await loadPosts();
    
    autoPublishToggle.addEventListener('change', async (e) => {
        const isChecked = e.target.checked;
        await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ auto_publish: isChecked })
        });
    });
}

async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        const data = await res.json();
        autoPublishToggle.checked = data.auto_publish;
    } catch (err) {
        console.error("Failed to load settings", err);
    }
}

async function loadPosts() {
    try {
        const res = await fetch('/api/posts');
        currentPosts = await res.json();
        renderPosts();
    } catch (err) {
        console.error("Failed to load posts", err);
    }
}

function renderPosts() {
    postGrid.innerHTML = '';
    
    // Sort logic: pending first, then by day
    const sortedPosts = currentPosts
        .filter(p => !p.published) // Hide published ones or show with different style
        .sort((a, b) => a.day - b.day);

    sortedPosts.forEach(post => {
        const isApproved = post.approved;
        
        const card = document.createElement('div');
        card.className = `post-card ${isApproved ? 'approved' : ''}`;
        
        card.innerHTML = `
            <div class="approval-badge">✓ APPROVED</div>
            <div class="card-header">
                <span class="card-title">Day ${post.day}</span>
                <div class="card-actions">
                    <button class="icon-btn approve" onclick="toggleApproval(${post.day})" title="Toggle Approval">
                        ${isApproved ? '☑' : '☐'}
                    </button>
                    <button class="icon-btn edit" onclick="openEditModal(${post.day})" title="Edit">✎</button>
                    <button class="icon-btn delete" onclick="deletePost(${post.day})" title="Delete">🗑</button>
                </div>
            </div>
            <div class="card-body">
                <div><span class="field">Book:</span> <span class="value">${post.book_title || 'N/A'}</span></div>
                <div><span class="field">Hook:</span> <span class="value">${post.hook}</span></div>
                <div><span class="field">Caption:</span> <span class="value">${post.caption}</span></div>
                <div class="hashtags">${post.hashtags}</div>
            </div>
        `;
        postGrid.appendChild(card);
    });
}

async function toggleApproval(day) {
    const post = currentPosts.find(p => p.day === day);
    if (!post) return;
    
    const updatedPost = {
        ...post,
        approved: !post.approved
    };
    
    await fetch(`/api/posts/${day}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedPost)
    });
    
    await loadPosts();
}

async function deletePost(day) {
    if(!confirm(`Are you sure you want to delete Day ${day} permanently?`)) return;
    
    await fetch(`/api/posts/${day}`, { method: 'DELETE' });
    await loadPosts();
}

function openEditModal(day) {
    const post = currentPosts.find(p => p.day === day);
    if (!post) return;
    
    currentEditingDay = day;
    modalDayNumber.textContent = day;
    editHook.value = post.hook;
    editCaption.value = post.caption;
    editHashtags.value = post.hashtags;
    
    editModal.classList.add('active');
}

function closeModal() {
    editModal.classList.remove('active');
    currentEditingDay = null;
}

async function savePostEdit() {
    const post = currentPosts.find(p => p.day === currentEditingDay);
    if (!post) return;
    
    const updatedPost = {
        ...post,
        hook: editHook.value,
        caption: editCaption.value,
        hashtags: editHashtags.value
    };
    
    await fetch(`/api/posts/${currentEditingDay}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedPost)
    });
    
    closeModal();
    await loadPosts();
}

// Start
init();
