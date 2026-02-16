import api from "./api";

export function getMyProfile() {
  return api.get("/accounts/my-profile/");
}

export function updateMyProfile(formData) {
  return api.patch("/accounts/my-profile/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
