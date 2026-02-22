/**
 * Social Saver Bot - Main JavaScript
 * Handles dashboard interactions, API calls, and UI functionality
 */

// Toast notification system
function showToast(message, type = 'success') {
    const container = document.getElementById('toast');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast-item ${type}`;
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Helper: safely convert any value to a displayable string
function safeString(value) {
    if (value === null || value === undefined) return '';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
}

// Add content form handler
document.getElementById('addContentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = document.getElementById('contentUrl').value;
    const btn = e.target.querySelector('button');
    const originalText = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

    try {
        const response = await fetch('/api/content', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Content saved successfully!', 'success');
            document.getElementById('contentUrl').value = '';
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(data.error || 'Failed to save content', 'error');
        }
    } catch (err) {
        showToast('An error occurred', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
});

// Delete content
async function deleteContent(id) {
    if (!confirm('Are you sure you want to delete this content?')) return;

    try {
        const response = await fetch(`/api/content/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            showToast('Content deleted', 'success');
            const card = document.getElementById(`card-${id}`);
            if (card) {
                card.style.transition = 'opacity 0.3s, transform 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.95)';
                setTimeout(() => { card.remove(); }, 300);
            } else {
                setTimeout(() => location.reload(), 500);
            }
        } else {
            showToast('Failed to delete content', 'error');
        }
    } catch (err) {
        showToast('An error occurred', 'error');
    }
}

// Regenerate AI content (category, summary, tags)
async function regenerateAI(id) {
    if (!confirm('Regenerate AI summary, category, and tags for this content?')) return;

    const btn = document.querySelector(`[onclick="regenerateAI(${id})"]`);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }

    try {
        const response = await fetch(`/api/content/${id}/regenerate`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showToast('AI content regenerated!', 'success');
            setTimeout(() => location.reload(), 500);
        } else {
            showToast(data.error || 'Failed to regenerate AI content', 'error');
        }
    } catch (err) {
        showToast('An error occurred', 'error');
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-magic"></i>'; }
    }
}

// Edit content - open modal and load data
async function editContent(id) {
    try {
        const response = await fetch(`/api/content/${id}`);
        const data = await response.json();

        if (data.success) {
            const content = data.data;

            document.getElementById('editId').value = content.id;
            document.getElementById('editTitle').value = safeString(content.title);

            // ── FIX: caption was showing [object Object] ──
            // Use summary if caption is empty/missing, fall back to empty string
            const caption = safeString(content.caption) || safeString(content.summary);
            document.getElementById('editCaption').value = caption;

            document.getElementById('editCategory').value = safeString(content.category) || 'Other';
            document.getElementById('editTags').value = safeString(content.tags);
            document.getElementById('editModal').classList.add('active');
        } else {
            showToast('Failed to load content', 'error');
        }
    } catch (err) {
        showToast('An error occurred', 'error');
    }
}

// Close modal
function closeModal() {
    document.getElementById('editModal').classList.remove('active');
}

// Close modal on outside click
document.getElementById('editModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'editModal') closeModal();
});

// Edit form submission
document.getElementById('editForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('editId').value;
    const data = {
        title: document.getElementById('editTitle').value,
        caption: document.getElementById('editCaption').value,
        category: document.getElementById('editCategory').value,
        tags: document.getElementById('editTags').value
    };

    try {
        const response = await fetch(`/api/content/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Content updated successfully!', 'success');
            closeModal();
            setTimeout(() => location.reload(), 500);
        } else {
            showToast('Failed to update content', 'error');
        }
    } catch (err) {
        showToast('An error occurred', 'error');
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        document.getElementById('contentUrl')?.focus();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('Social Saver Bot initialized');
});
