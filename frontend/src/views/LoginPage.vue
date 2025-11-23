<template>
  <div class="auth-page">
    <Toast />

    <section v-if="!user" class="auth-card">
      <h2>Welcome back</h2>
      <p class="auth-description">Sign in or create a new pwRank account.</p>

      <div class="auth-form" @keyup.enter="login">
        <span class="p-input-icon-left">
          <i class="pi pi-envelope" />
          <InputText
            v-model="email"
            id="email"
            type="email"
            placeholder="Email"
          />
        </span>
        <Password
          v-model="password"
          id="password"
          placeholder="Password"
          :toggleMask="true"
          :feedback="false"
          autocomplete="current-password"
        />
      </div>

      <div class="auth-actions">
        <Button
          label="Login"
          icon="pi pi-sign-in"
          @click="login"
          :loading="loading"
          :disabled="!isLoginFormValid"
        />
        <Button
          label="Register"
          icon="pi pi-user-plus"
          class="p-button-secondary"
          @click="register"
          :loading="loading"
          :disabled="!isRegisterFormValid"
        />
      </div>
    </section>

    <section v-else class="auth-card">
      <h2>Signed in as {{ user.identity.email }}</h2>
      <p class="auth-description">
        You are successfully authenticated.
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
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { REST, HttpError } from "../rest";
import { MIN_PASSWORD_LENGTH } from "../constants";
import { useNotification } from "../composables/useNotification";
import { useFormValidation } from "../composables/useFormValidation";

const email = ref("");
const password = ref("");
const session = ref(REST.userIdentity());
const loading = ref(false);

const { notifySuccess, notifyError, notifyInfo, notifyWarn } = useNotification();
const { isValidEmail, isPasswordValid } = useFormValidation();

const router = useRouter();
const route = useRoute();

const redirectTarget = computed(() => {
  const redirect = route.query.redirect;
  return typeof redirect === "string" ? redirect : null;
});

const user = computed(() => session.value);

const isLoginFormValid = computed(() => {
  return isValidEmail(email.value) && password.value.length >= 1;
});

const isRegisterFormValid = computed(() => {
  return isValidEmail(email.value) && isPasswordValid(password.value);
});

async function login() {
  if (!isLoginFormValid.value || loading.value) return;

  loading.value = true;
  try {
    const result = await REST.login(email.value, password.value);
    if (!result.ok) {
      notifyError(result.message, "Login failed");
      return;
    }

    session.value = REST.userIdentity();
    notifySuccess("Logged in");

    if (redirectTarget.value) {
      router.push(redirectTarget.value);
    } else {
      router.push({ name: "Rankings" });
    }
  } finally {
    loading.value = false;
  }
}

async function register() {
  if (!isRegisterFormValid.value || loading.value) return;

  loading.value = true;
  try {
    const data = await REST.post("/auth/user", {
      email: email.value,
      password: password.value,
    });
    notifySuccess("Registration successful", data.message ?? "");
  } catch (error) {
    notifyError(error, "Registration failed");
  } finally {
    loading.value = false;
  }
}

async function refresh() {
  const refreshed = await REST.refreshToken();
  session.value = REST.userIdentity();

  if (refreshed) {
    notifySuccess("Token refreshed");
  } else {
    notifyWarn("Refresh failed", "Please log in again.");
  }
}

function logout() {
  REST.logout();
  session.value = null;
  notifyInfo("Logged out");
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
</style>
