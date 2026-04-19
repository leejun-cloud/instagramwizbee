let currentPosts = [];
let currentFilter = 'all';

// Element Selectors
const postGrid = document.getElementById('postGrid');
const editModal = document.getElementById('editModal');
const modalDayNumber = document.getElementById('modalDayNumber');
const editHook = document.getElementById('editHook');
const editCaption = document.getElementById('editCaption');
const editHashtags = document.getElementById('editHashtags');
const seedBtn = document.getElementById('seedBtn');

let currentEditingDay = null;

// Initialize App
async function init() {
    console.log("🚀 Starting Cloud Dashboard (RTDB Edition)...");
    
    // Check if we are running locally to show the "Seed" button
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        seedBtn.style.display = 'inline-block';
    }

    // Real-time listener for Realtime Database
    const postsRef = window.dbRef(window.rtdb, 'posts');
    window.onValue(postsRef, (snapshot) => {
        const data = snapshot.val();
        if (data) {
            currentPosts = Object.values(data);
        } else {
            currentPosts = [];
        }
        renderPosts();
    });

    // Add Filter Listeners
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            currentFilter = e.target.getAttribute('data-filter');
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            renderPosts();
        });
    });
}

function renderPosts() {
    postGrid.innerHTML = '';
    
    let filtered = currentPosts.sort((a, b) => b.day - a.day);
    
    if (currentFilter === 'pending') {
        filtered = filtered.filter(p => !p.published);
    } else if (currentFilter === 'published') {
        filtered = filtered.filter(p => p.published);
    }

    if (filtered.length === 0) {
        postGrid.innerHTML = '<div class="empty-state">No posts found in the Cloud RTDB. Please use the [Seed] button locally.</div>';
        return;
    }

    filtered.forEach(post => {
        const card = document.createElement('div');
        card.className = `post-card ${post.published ? 'published' : ''} ${post.approved ? 'approved' : ''}`;
        
        const badges = [];
        if (post.published) badges.push('<span class="badge badge-published">LIVE</span>');
        else badges.push('<span class="badge badge-pending">DRAFT</span>');
        if (post.approved && !post.published) badges.push('<span class="badge badge-approved">APPROVED</span>');

        card.innerHTML = `
            ${badges.join('')}
            <div class="card-title">
                Day ${post.day} ${post.type === 'carousel' ? '🎠' : '📸'}
                <span class="scheduled-date">${post.scheduled_date || 'No Date'}</span>
            </div>
            <div class="card-image-preview">
                <img src="/images/day_${post.day}.jpg"
                     data-day="${post.day}"
                     onerror="window.handleImgFallback(this)"
                     class="single-thumb">
            </div>
            <div class="card-body">
                <p><strong>Hook:</strong> ${post.hook}</p>
            </div>
            <div class="card-actions">
                ${!post.published ? `
                    <button class="action-btn approve-btn ${post.approved ? 'is-approved' : ''}" onclick="window.toggleApproval(${post.day})">
                        ${post.approved ? 'Approved' : 'Approve'}
                    </button>
                ` : ''}
                <button class="action-btn" onclick="window.openEditModal(${post.day})">Edit</button>
            </div>
        `;
        postGrid.appendChild(card);
    });
}

// Image fallback chain: day_N.jpg → day_N.png → test_image.png.
// Uses a data-step attribute so a single onerror handler never loops.
window.handleImgFallback = function(img) {
    const step = img.dataset.step || "0";
    const day = img.dataset.day;
    if (step === "0") {
        img.dataset.step = "1";
        img.src = `/images/day_${day}.png`;
    } else if (step === "1") {
        img.dataset.step = "2";
        img.src = "/images/test_image.png";
    } else {
        img.onerror = null; // give up, avoid infinite loop
    }
};

// Actions
window.toggleApproval = async function(day) {
    const post = currentPosts.find(p => p.day === day);
    if (!post) return;
    const postRef = window.dbRef(window.rtdb, `posts/${day}`);
    await window.dbUpdate(postRef, { approved: !post.approved });
};

window.openEditModal = function(day) {
    const post = currentPosts.find(p => p.day === day);
    if (!post) return;
    currentEditingDay = day;
    modalDayNumber.textContent = day;
    editHook.value = post.hook;
    editCaption.value = post.caption;
    editHashtags.value = post.hashtags;
    editModal.classList.add('active');
};

window.closeModal = function() {
    editModal.classList.remove('active');
};

window.savePostEdit = async function() {
    if (!currentEditingDay) return;
    const postRef = window.dbRef(window.rtdb, `posts/${currentEditingDay}`);
    await window.dbUpdate(postRef, {
        hook: editHook.value,
        caption: editCaption.value,
        hashtags: editHashtags.value
    });
    closeModal();
};

// Seed Local Data to Cloud
window.seedLocalData = async function() {
    if (!confirm("Seed local 'book_data.json' to Cloud Realtime DB? This will overwrite cloud data.")) return;
    try {
        const response = await fetch('book_data.json');
        const data = await response.json();
        
        const updates = {};
        for (const post of data) {
            updates[`posts/${post.day}`] = post;
        }
        
        const rootRef = window.dbRef(window.rtdb);
        await window.dbUpdate(rootRef, updates);
        
        alert("Cloud Sync (RTDB) Successful! All local data is now in the Cloud.");
    } catch (err) {
        alert("Seed failed. Ensure you are running locally via python -m http.server 5001");
        console.error(err);
    }
};

window.generateBatch = function() {
    alert("Batch generation is a heavy process. Please run 'python3 batch_generator.py' on your laptop.");
};

window.loadPosts = function() {
    location.reload();
};

init();
