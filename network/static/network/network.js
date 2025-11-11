function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

document.addEventListener("DOMContentLoaded", () => {
  // New post form (AJAX)
  const newPostForm = document.getElementById("new-post-form");
  if (newPostForm) {
    newPostForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const content = document.getElementById("new-post-content").value.trim();
      if (!content) return alert("Type something to post.");

      const resp = await fetch("/posts/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ content }),
      });

      if (resp.ok) {
        const data = await resp.json();
        const post = data.post;
        const container = document.querySelector(".container");

        const card = document.createElement("div");
        card.className = "card mb-3 post-card";
        card.dataset.postId = post.id;
        card.innerHTML = `
          <div class="card-body">
            <h6><a href="/profile/${post.author}">${post.author}</a>
            <small class="text-muted"> — ${post.timestamp}</small></h6>
            <div class="post-content"><p class="mb-2">${escapeHtml(post.content)}</p></div>
            <div class="d-flex align-items-center">
              <button class="btn btn-sm btn-outline-primary like-btn" data-liked="false"><span class="like-count">0</span> ♥</button>
              <button class="btn btn-sm btn-outline-secondary ml-2 edit-btn">Edit</button>
              <button class="btn btn-sm btn-info ml-2 toggle-comments-btn">Comments</button>
            </div>
            <div class="comments-section mt-3 d-none">
              <div class="existing-comments"><p class="text-muted">No comments yet.</p></div>
              <form class="comment-form mt-2" data-post-id="${post.id}">
                <input type="text" class="form-control form-control-sm comment-input" placeholder="Write a comment...">
                <button type="submit" class="btn btn-sm btn-primary mt-1">Comment</button>
              </form>
            </div>
          </div>`;
        container.prepend(card);
        document.getElementById("new-post-content").value = "";
      } else {
        const err = await resp.json();
        alert(err.error || "Could not create post.");
      }
    });
  }

  // Like / Edit / Comment Toggle Delegation
  document.addEventListener("click", async (e) => {
    const likeBtn = e.target.closest(".like-btn");
    const editBtn = e.target.closest(".edit-btn");
    const toggleBtn = e.target.closest(".toggle-comments-btn");

    // Like
    if (likeBtn) {
      const postCard = likeBtn.closest(".post-card");
      const postId = postCard.dataset.postId;
      const resp = await fetch(`/posts/${postId}/like`, {
        method: "PUT",
        headers: { "X-CSRFToken": csrftoken },
      });
      if (resp.ok) {
        const data = await resp.json();
        likeBtn.dataset.liked = data.liked ? "true" : "false";
        likeBtn.querySelector(".like-count").textContent = data.likes_count;
      }
      return;
    }

    // Edit
    if (editBtn) {
      const postCard = editBtn.closest(".post-card");
      const postId = postCard.dataset.postId;
      const contentDiv = postCard.querySelector(".post-content");
      const original = contentDiv.innerText.trim();
      const textarea = document.createElement("textarea");
      textarea.className = "form-control mb-2 edit-textarea";
      textarea.value = original;
      contentDiv.innerHTML = "";
      contentDiv.appendChild(textarea);
      editBtn.textContent = "Save";
      editBtn.classList.add("save-btn");
      editBtn.classList.remove("edit-btn");

      const onSave = async () => {
        const newContent = textarea.value.trim();
        if (!newContent) return alert("Content cannot be empty.");
        const resp = await fetch(`/posts/${postId}/edit`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify({ content: newContent }),
        });
        if (resp.ok) {
          const data = await resp.json();
          contentDiv.innerHTML = `<p class="mb-2">${escapeHtml(data.content)}</p>`;
          editBtn.textContent = "Edit";
          editBtn.classList.add("edit-btn");
          editBtn.classList.remove("save-btn");
          editBtn.removeEventListener("click", onSave);
        } else {
          alert("Could not save post.");
        }
      };
      editBtn.addEventListener("click", onSave);
      return;
    }

    // Toggle Comments
    if (toggleBtn) {
      const section = toggleBtn.closest(".post-card").querySelector(".comments-section");
      section.classList.toggle("d-none");
      return;
    }
  });

  // Follow button
  const followBtn = document.getElementById("follow-button");
  if (followBtn) {
    followBtn.addEventListener("click", async () => {
      const username = followBtn.dataset.username;
      const resp = await fetch(`/profile/${username}/follow`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
      });
      if (resp.ok) {
        const data = await resp.json();
        followBtn.textContent = data.following ? "Unfollow" : "Follow";
        const followersCount = document.getElementById("followers-count");
        if (followersCount) followersCount.textContent = data.followers_count;
      }
    });
  }
});

// Comment submit (AJAX)
document.addEventListener("submit", async (e) => {
  const form = e.target.closest(".comment-form");
  if (!form) return;
  e.preventDefault();
  const postId = form.dataset.postId;
  const input = form.querySelector(".comment-input");
  const content = input.value.trim();
  if (!content) return alert("Comment cannot be empty.");

  const resp = await fetch(`/posts/${postId}/comment`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ content }),
  });

  if (resp.ok) {
    const data = await resp.json();
    const commentsDiv = form.closest(".post-card").querySelector(".existing-comments");
    const p = document.createElement("p");
    p.innerHTML = `<strong>${data.author}</strong>: ${escapeHtml(data.content)}`;
    commentsDiv.appendChild(p);
    input.value = "";
  } else {
    const err = await resp.json();
    alert(err.error || "Could not post comment.");
  }
});

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>"'`=\/]/g, function (s) {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
      "/": "&#x2F;",
      "`": "&#x60;",
      "=": "&#x3D;",
    }[s];
  });
}
