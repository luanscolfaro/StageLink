import api from "./api";

export function getFeed() {
  return api.get("/social/posts/");
}

export function createPost(content, image) {
    const form = new FormData();
    form.append("content", content || "");
    if (image) form.append("image", image);
  
    return api.post("/social/posts/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }
  
  

export function likePost(postId) {
  return api.post(`/social/posts/${postId}/like/`);
}

export function unlikePost(postId) {
  return api.post(`/social/posts/${postId}/unlike/`);
}

export function getComments(postId) {
  return api.get(`/social/posts/${postId}/comments/`);
}

export function addComment(postId, text) {
  return api.post(`/social/posts/${postId}/comments/`, { text });
}

export function getUserPosts(username) {
  return api.get(`/social/posts/?author=${encodeURIComponent(username)}`);
}

