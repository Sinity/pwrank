<template>
  <div class="ranking-page">
    <header class="ranking-page__header">
      <h2 v-if="ranking">Ranking: {{ ranking.name }}</h2>
      <div class="ranking-page__actions">
        <Button
          icon="pi pi-sync"
          label="Sync items"
          @click="openSyncDialog"
          :disabled="!ranking"
        />
        <Button
          icon="pi pi-arrow-right"
          label="Compare"
          class="p-button-secondary"
          @click="router.push({ name: 'Comparing', params: { id: rankingId } })"
        />
      </div>
    </header>

    <Dialog
      v-if="ranking"
      v-model:visible="displaySyncModal"
      :header="`Sync items from ${ranking.datasource}`"
      :style="{ width: '50vw' }"
      :modal="true"
    >
      <div v-if="ranking.datasource === 'anilist'" class="p-fluid">
        <div class="p-field p-grid">
          <label class="p-col-12 p-md-3" for="anilist_username">Username</label>
          <div class="p-col-12 p-md-9">
            <InputText
              id="anilist_username"
              v-model="anilistUsername"
              type="text"
              placeholder="Username"
            />
          </div>
        </div>
        <div class="p-field p-grid">
          <label class="p-col-12 p-md-3" for="anilist_status">Statuses</label>
          <div class="p-col-12 p-md-9">
            <MultiSelect
              v-model="anilistStatuses"
              :options="anilistStatusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Status"
              display="chip"
            />
          </div>
        </div>
      </div>

      <div v-else-if="ranking.datasource === 'steam'" class="p-fluid">
        <div class="p-field p-grid">
          <label class="p-col-12 p-md-3" for="steam_id">Steam ID</label>
          <div class="p-col-12 p-md-9">
            <InputText
              id="steam_id"
              v-model="steamId"
              type="text"
              placeholder="Steam ID"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="Submit"
          icon="pi pi-check"
          @click="syncItems"
          :loading="syncing"
          autofocus
        />
      </template>
    </Dialog>

    <DataTable :value="items" :loading="loading">
      <Column field="img_url" header="Image">
        <template #body="{ data }">
          <img :src="data.img_url" :alt="data.label" width="80" />
        </template>
      </Column>
      <Column field="label" header="Label" :sortable="true" />
      <Column field="curr_rating" header="Current rating" :sortable="true" />
      <Column field="init_rating" header="Initial rating" :sortable="true" />
      <Column field="stderr" header="Standard error" :sortable="true" />
    </DataTable>
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

const ranking = ref(null);
const items = ref([]);
const rankingId = ref(route.params.id);
const loading = ref(false);
const syncing = ref(false);

const displaySyncModal = ref(false);
const steamId = ref("");
const anilistUsername = ref("");
const anilistStatuses = ref([]);

const anilistStatusOptions = [
  { label: "Current", value: "CURRENT" },
  { label: "Planning", value: "PLANNING" },
  { label: "Paused", value: "PAUSED" },
  { label: "Completed", value: "COMPLETED" },
  { label: "Dropped", value: "DROPPED" },
  { label: "Repeating", value: "REPEATING" },
];

watch(
  () => route.params.id,
  (id) => {
    rankingId.value = id;
    loadRanking();
  }
);

function openSyncDialog() {
  steamId.value = "";
  anilistUsername.value = "";
  anilistStatuses.value = [];
  displaySyncModal.value = true;
}

async function loadRanking() {
  loading.value = true;
  try {
    const data = await REST.get(`/ranking/${rankingId.value}`);
    ranking.value = data.ranking;
    items.value = data.ranking?.items ?? [];
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to load ranking",
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

async function syncItems() {
  if (!ranking.value) return;

  syncing.value = true;
  const payload = {
    anilist_username: anilistUsername.value,
    anilist_statuses: anilistStatuses.value,
    steam_id: steamId.value,
  };

  try {
    await REST.post(`/ranking/${rankingId.value}`, payload);
    toast.add({
      severity: "success",
      summary: "Items synced",
      detail: "",
      life: 2000,
    });
    await loadRanking();
    displaySyncModal.value = false;
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Sync failed",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: 4000,
    });
  } finally {
    syncing.value = false;
  }
}

onMounted(loadRanking);
</script>

<style scoped>
.ranking-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.ranking-page__header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.ranking-page__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
</style>
