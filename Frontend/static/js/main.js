// Shared utility: authenticated fetch
function authFetch(url, options = {}) {
  const token = localStorage.getItem("token");
  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
}

// Redirect to login if no token (call on protected pages)
function requireAuth() {
  if (!localStorage.getItem("token")) {
    window.location.href = "/login";
  }
}
