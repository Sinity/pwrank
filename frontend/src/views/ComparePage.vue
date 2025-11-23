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

    <div v-if="!message && items.length === 2" class="compare-hint">
      <i class="pi pi-info-circle"></i>
      <span>Click your preferred item or press <kbd>1</kbd> / <kbd>←</kbd> for left, <kbd>2</kbd> / <kbd>→</kbd> for right</span>
    </div>

    <p v-if="message" class="compare-page__message">{{ message }}</p>

    <div v-if="!message" class="compare-page__grid">
      <Panel
        v-for="(item, index) in items"
        :key="item.id"
        class="compare-card"
        :toggleable="false"
        @click="submitComparison(item.id, opponentId(item.id))"
        tabindex="0"
        @keyup.enter="submitComparison(item.id, opponentId(item.id))"
      >
        <template #header>
          <h2>{{ item.label }} <span class="keyboard-hint">({{ index + 1 }})</span></h2>
        </template>
        <img
          :src="item.img_url || FALLBACK_IMAGE_SVG"
          :alt="item.label"
          @error="(e) => e.target.src = FALLBACK_IMAGE_SVG"
        />
      </Panel>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";

import { REST, HttpError } from "../rest";
import { FALLBACK_IMAGE_SVG, TOAST_DURATION_SHORT, TOAST_DURATION_LONG } from "../constants";

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
      life: TOAST_DURATION_SHORT,
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
      life: TOAST_DURATION_LONG,
    });
  } finally {
    loading.value = false;
  }
}

function handleKeyPress(event) {
  if (loading.value || message.value || items.value.length !== 2) return;

  if (event.key === "1" || event.key === "ArrowLeft") {
    event.preventDefault();
    const first = items.value[0];
    const second = items.value[1];
    if (first && second) {
      submitComparison(first.id, second.id);
    }
  } else if (event.key === "2" || event.key === "ArrowRight") {
    event.preventDefault();
    const first = items.value[0];
    const second = items.value[1];
    if (first && second) {
      submitComparison(second.id, first.id);
    }
  }
}

onMounted(() => {
  loadComparison();
  window.addEventListener("keydown", handleKeyPress);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyPress);
});
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

.keyboard-hint {
  font-size: 0.8em;
  color: var(--primary-color);
  font-weight: normal;
}

.compare-hint {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background-color: rgba(var(--primary-color-rgb, 59, 130, 246), 0.1);
  border-left: 4px solid var(--primary-color);
  border-radius: 4px;
  color: var(--text-color);
  font-size: 0.95rem;
}

.compare-hint i {
  color: var(--primary-color);
  font-size: 1.25rem;
}

.compare-hint kbd {
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  background-color: var(--surface-100);
  border: 1px solid var(--surface-300);
  font-family: monospace;
  font-size: 0.9em;
}
</style>
