<template>
  <div class="compare-page">
    <div class="compare-page__actions">
      <Button
        icon="pi pi-arrow-left"
        label="Ranking info"
        @click="router.push({ name: 'Ranking', params: { id: rankingId } })"
      />
      <Button
        icon="pi pi-refresh"
        label="Refresh"
        class="p-button-secondary"
        :disabled="loading"
        @click="loadComparison"
      />
    </div>

    <p v-if="message" class="compare-page__message">{{ message }}</p>

    <div v-if="!message" class="compare-page__grid">
      <Panel
        v-for="item in items"
        :key="item.id"
        class="compare-card"
        :toggleable="false"
        @click="submitComparison(item.id, opponentId(item.id))"
      >
        <template #header>
          <h2>{{ item.label }}</h2>
        </template>
        <img :src="item.img_url" :alt="item.label" />
      </Panel>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";

import { REST, HttpError } from "../rest";

const route = useRoute();
const router = useRouter();
const toast = useToast();

const rankingId = ref(route.params.id);
const items = ref([]);
const loading = ref(false);
const message = ref("");

const opponentId = (id) => {
  const [first, second] = items.value;
  return first?.id === id ? second?.id : first?.id;
};

watch(
  () => route.params.id,
  (id) => {
    rankingId.value = id;
    loadComparison();
  }
);

async function loadComparison() {
  loading.value = true;
  message.value = "";
  items.value = [];
  try {
    const data = await REST.get(`/compare/${rankingId.value}`);
    const comparison = data?.comparison || [];
    if (comparison.length < 2) {
      message.value = "Not enough items for comparison yet.";
    } else {
      items.value = comparison;
    }
  } catch (error) {
    message.value =
      error instanceof HttpError
        ? error.payload?.message || "Unable to load comparison."
        : "Unable to reach the backend.";
  } finally {
    loading.value = false;
  }
}

async function submitComparison(winnerId, loserId) {
  if (!winnerId || !loserId) {
    return;
  }

  loading.value = true;
  try {
    await REST.post(`/compare/${rankingId.value}`, {
      winitem: winnerId,
      loseitem: loserId,
    });
    toast.add({
      severity: "success",
      summary: "Comparison saved",
      detail: "",
      life: 1500,
    });
    await loadComparison();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to submit comparison",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: 4000,
    });
  } finally {
    loading.value = false;
  }
}

onMounted(loadComparison);
</script>

<style scoped>
.compare-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.compare-page__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.compare-page__message {
  font-size: 1rem;
  color: var(--text-color-secondary);
}

.compare-page__grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.compare-card {
  cursor: pointer;
  text-align: center;
}

.compare-card img {
  width: 100%;
  max-height: 320px;
  object-fit: cover;
  border-radius: 0.75rem;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.35);
}
</style>
