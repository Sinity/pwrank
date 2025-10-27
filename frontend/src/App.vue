<template>
  <div class="app-shell">
    <header class="app-shell__nav">
      <Menubar :model="menuItems" />
    </header>
    <main class="app-shell__page">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";

const menuItems = [
  { label: "Account", to: "/login" },
  { label: "Rankings", to: "/rankings" },
];
</script>

<style>
:root {
  color-scheme: dark;
}

:global(body) {
  margin: 0;
  min-height: 100vh;
  background-color: var(--surface-f);
  font-family: var(--font-family);
  font-weight: 400;
  color: var(--text-color);
}

.app-shell {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-shell__nav {
  padding: 2rem;
  text-align: center;
  background-color: var(--surface-a);
}

.app-shell__page {
  flex: 1;
  background-color: var(--surface-b);
  padding: 2rem;
}

.app-shell__nav a {
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--secondary-color);
}

.app-shell__nav a.router-link-exact-active {
  color: var(--primary-color);
}
</style>
