import api from "./api"; // <-- tem que ser o MESMO api que você já usa no projeto

export function searchUsers(q) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  return api.get(`/social/users/search/${qs}`);
}

export function getProfile(username) {
  return api.get(`/social/profile/${encodeURIComponent(username)}/`);
}

export function getFollowers(username) {
  return api.get(`/social/profile/${encodeURIComponent(username)}/followers/`);
}

export function getFollowing(username) {
  return api.get(`/social/profile/${encodeURIComponent(username)}/following/`);
}

export function followUser(userId) {
  return api.post(`/social/follow/${userId}/`);
}

export function unfollowUser(userId) {
  return api.post(`/social/unfollow/${userId}/`);
}

export function getReviews(username) {
  return api.get(`/social/profile/${encodeURIComponent(username)}/reviews/`);
}

export function submitReview(username, rating, text) {
  return api.post(`/social/profile/${encodeURIComponent(username)}/reviews/`, { rating, text });
}
