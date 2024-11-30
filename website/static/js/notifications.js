document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializeNotificationSystem();
});

function initializeNotificationSystem() {
    // Update notification badge on page load
    updateNotificationCount();
    
    // Add click handlers for notification items
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            if (notificationId) {
                markAsRead(notificationId);
            }
        });
    });

    // Add handler for mark all as read
    const markAllReadBtn = document.querySelector('.mark-all-read');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllAsRead();
        });
    }
}

function initializeWebSocket() {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const notificationSocket = new WebSocket(
        ws_scheme + '://' + window.location.host + '/ws/notifications/'
    );

    notificationSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('Received notification:', data);

        if (data.type === 'notification') {
            handleNewNotification(data);
        }
    };

    notificationSocket.onclose = function(e) {
        console.log('WebSocket closed unexpectedly');
        setTimeout(initializeWebSocket, 3000);
    };

    notificationSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };
}

function handleNewNotification(data) {
    playNotificationSound();
    shakeBell();
    incrementNotificationCount();
    addNotificationToList(data);
}

function markAllAsRead() {
    fetch('/website/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Mark all notifications as read in UI
            document.querySelectorAll('.notification-item.unread').forEach(item => {
                item.classList.remove('unread');
            });
            updateNotificationCount();
        }
    })
    .catch(error => console.error('Error marking all as read:', error));
}

function markAsRead(notificationId) {
    fetch(`/notifications/${notificationId}/read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notification) {
                notification.classList.remove('unread');
                updateNotificationCount();
            }
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

function updateNotificationCount() {
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;
    const badge = document.getElementById('notification-count');
    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'block' : 'none';
    }
}

function playNotificationSound() {
    const sound = document.getElementById('notificationSound');
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(err => console.log('Error playing sound:', err));
    }
}

function shakeBell() {
    const bell = document.querySelector('.notification-icon');
    if (bell) {
        bell.classList.add('bell-shake');
        setTimeout(() => bell.classList.remove('bell-shake'), 1000);
    }
}

function incrementNotificationCount() {
    const badge = document.getElementById('notification-count');
    if (badge) {
        const currentCount = parseInt(badge.textContent || '0');
        badge.textContent = currentCount + 1;
        badge.style.display = 'block';
    }
}

function addNotificationToList(data) {
    const list = document.getElementById('notification-list');
    if (!list) return;

    const newNotification = `
        <div class="notification-item unread" data-notification-id="${data.notification_id}">
            <div class="notification-content p-2">
                <p class="mb-1">${data.message}</p>
                <small class="text-muted">just now</small>
                ${data.record_id ? `
                    <a href="/record/${data.record_id}/" class="btn btn-sm btn-link p-0">
                        View Record
                    </a>
                ` : ''}
            </div>
        </div>`;

    // Insert at the beginning of the list
    const firstItem = list.firstChild;
    if (firstItem) {
        firstItem.insertAdjacentHTML('beforebegin', newNotification);
    } else {
        list.innerHTML = newNotification;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
  