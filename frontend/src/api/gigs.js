import api from "./api";

export function listGigs(params = {}) {
  // params: { city, tag }
  return api.get("/gigs/gigs/", { params });
}

export function createGig(payload) {
  // payload: { title, description, city, date, fee, tags }
  return api.post("/gigs/gigs/", payload);
}

export function applyGig(gigId, message) {
  return api.post(`/gigs/gigs/${gigId}/apply/`, { message });
}

export function getGigApplications(gigId) {
  return api.get(`/gigs/gigs/${gigId}/applications/`);
}

export function acceptApplication(appId) {
  return api.post(`/gigs/applications/${appId}/accept/`);
}

export function rejectApplication(appId) {
  return api.post(`/gigs/applications/${appId}/reject/`);
}
