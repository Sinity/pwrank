<template>
  <div class="auth-page">
    <Toast />

    <section v-if="!user" class="auth-card">
      <h2>Welcome back</h2>
      <p class="auth-description">Sign in or create a new pwRank account.</p>

      <div class="auth-form">
        <span class="p-input-icon-left">
          <i class="pi pi-envelope" />
          <InputText
            v-model="email"
            id="email"
            type="email"
            placeholder="Email"
          />
        </span>
        <span class="p-input-icon-left">
          <i class="pi pi-lock" />
          <InputText
            v-model="password"
            id="password"
            type="password"
            placeholder="Password"
            autocomplete="current-password"
          />
        </span>
      </div>

      <div class="auth-actions">
        <Button label="Login" icon="pi pi-sign-in" @click="login" />
        <Button
          label="Register"
          icon="pi pi-user-plus"
          class="p-button-secondary"
          @click="register"
        />
      </div>
    </section>

    <section v-else class="auth-card">
      <h2>Signed in as {{ user.identity.email }}</h2>
      <p class="auth-description">
        Use the shortcuts below to manage your session.
      </p>

      <div class="auth-actions">
        <Button
          label="Refresh token"
          icon="pi pi-refresh"
          class="p-button-secondary"
          @click="refresh"
        />
        <Button
          label="Logout"
          icon="pi pi-sign-out"
          class="p-button-danger"
          @click="logout"
        />
      </div>

      <div class="auth-tokens">
        <p>
          <strong>User id:</strong>
          <code>{{ user.identity.id }}</code>
        </p>
        <p>
          <strong>Access token:</strong>
          <code>{{ user.accessToken }}</code>
        </p>
        <p>
          <strong>Refresh token:</strong>
          <code>{{ user.refreshToken }}</code>
        </p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";

import { REST, HttpError } from "../rest";

const email = ref("");
const password = ref("");
const session = ref(REST.userIdentity());

const toast = useToast();
const router = useRouter();
const route = useRoute();

const redirectTarget = computed(() => {
  const redirect = route.query.redirect;
  return typeof redirect === "string" ? redirect : null;
});

const user = computed(() => session.value);

function notify({ severity, summary, detail, life = 3000 }) {
  toast.add({ severity, summary, detail, life });
}

async function login() {
  const result = await REST.login(email.value, password.value);
  if (!result.ok) {
    notify({
      severity: "error",
      summary: "Login failed",
      detail: result.message,
      life: 4000,
    });
    return;
  }

  session.value = REST.userIdentity();
  notify({ severity: "success", summary: "Logged in", detail: "", life: 2000 });

  if (redirectTarget.value) {
    router.push(redirectTarget.value);
  } else {
    router.push({ name: "Rankings" });
  }
}

async function register() {
  try {
    const data = await REST.post("/auth/user", {
      email: email.value,
      password: password.value,
    });
    notify({
      severity: "success",
      summary: "Registration successful",
      detail: data.message ?? "",
      life: 3000,
    });
  } catch (error) {
    const detail =
      error instanceof HttpError
        ? error.payload?.message ?? "Registration failed."
        : "Unable to reach the backend.";
    notify({
      severity: "error",
      summary: "Registration failed",
      detail,
      life: 4000,
    });
  }
}

async function refresh() {
  const refreshed = await REST.refreshToken();
  session.value = REST.userIdentity();
  notify({
    severity: refreshed ? "success" : "warn",
    summary: refreshed ? "Token refreshed" : "Refresh failed",
    detail: refreshed ? "" : "Please log in again.",
    life: 3000,
  });
}

function logout() {
  REST.logout();
  session.value = null;
  notify({ severity: "info", summary: "Logged out", detail: "", life: 2000 });
}

onMounted(() => {
  session.value = REST.userIdentity();
});
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  padding: 3rem 1rem;
}

.auth-card {
  width: min(480px, 100%);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2.5rem;
  border-radius: 1rem;
  background-color: var(--surface-card);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
}

.auth-description {
  margin: 0;
  color: var(--text-color-secondary);
}

.auth-form {
  display: grid;
  gap: 1rem;
}

.auth-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: flex-start;
}

.auth-actions .p-button {
  flex: 1 1 45%;
  min-width: 9rem;
}

.auth-tokens {
  display: grid;
  gap: 0.75rem;
  background-color: var(--surface-b);
  padding: 1.5rem;
  border-radius: 0.75rem;
  font-size: 0.95rem;
  word-break: break-all;
}

code {
  display: block;
  padding-top: 0.25rem;
  color: var(--primary-color);
  font-size: 0.85rem;
}
</style>
