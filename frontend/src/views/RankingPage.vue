<template>
  <div class="ranking-page">
    <Toast />

    <header class="ranking-page__header">
      <div>
        <h2 v-if="ranking">Ranking: {{ ranking.name }}</h2>
        <p v-if="ranking" class="ranking-stats">
          <span>{{ ranking.item_count }} items</span>
          <span class="separator">•</span>
          <span>{{ ranking.comp_count }} comparisons</span>
          <span v-if="ranking.comp_count > 0 && ranking.item_count > 1" class="separator">•</span>
          <span v-if="ranking.comp_count > 0 && ranking.item_count > 1">
            {{ getCompletionPercentage() }}% complete
          </span>
        </p>
      </div>
      <div class="ranking-page__actions">
        <Button
          icon="pi pi-download"
          label="Export CSV"
          class="p-button-secondary"
          @click="exportToCSV"
          :disabled="!ranking || items.length === 0"
        />
        <Button
          icon="pi pi-sync"
          label="Sync items"
          @click="openSyncDialog"
          :disabled="!ranking"
        />
        <Button
          icon="pi pi-arrow-right"
          label="Compare"
          class="p-button-success"
          @click="router.push({ name: 'Comparing', params: { id: rankingId } })"
          :disabled="!ranking || items.length < 2"
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
      <div v-if="ranking.datasource === 'anilist'" class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="anilist_username">Username</label>
          <InputText
            id="anilist_username"
            v-model="anilistUsername"
            type="text"
            placeholder="Username"
          />
        </div>
        <div class="flex flex-column gap-2">
          <label for="anilist_status">Statuses</label>
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

      <div v-else-if="ranking.datasource === 'steam'" class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="steam_id">Steam ID</label>
          <InputText
            id="steam_id"
            v-model="steamId"
            type="text"
            placeholder="Steam ID"
          />
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

    <!-- Empty State -->
    <div v-if="!loading && items.length === 0" class="empty-state">
      <i class="pi pi-inbox" style="font-size: 4rem; color: var(--text-color-secondary)"></i>
      <h3>No Items Yet</h3>
      <p>Click "Sync items" to import items from {{ ranking?.datasource || 'external source' }}.</p>
      <Button
        icon="pi pi-sync"
        label="Sync Items"
        class="p-button-lg"
        @click="openSyncDialog"
      />
    </div>

    <!-- Search and Filter -->
    <div v-if="items.length > 0" class="search-controls">
      <span class="p-input-icon-left" style="flex: 1; max-width: 400px;">
        <i class="pi pi-search" />
        <InputText
          v-model="searchQuery"
          placeholder="Search items..."
          style="width: 100%"
        />
      </span>
      <Dropdown
        v-model="filterBy"
        :options="filterOptions"
        optionLabel="label"
        optionValue="value"
        placeholder="Filter by"
        style="width: 200px"
      />
    </div>

    <DataTable
      v-if="items.length > 0"
      :value="filteredItems"
      :loading="loading"
      :paginator="filteredItems.length > 20"
      :rows="20"
      sortField="curr_rating"
      :sortOrder="-1"
      stripedRows
    >
      <Column field="img_url" header="Image">
        <template #body="{ data }">
          <img :src="data.img_url" :alt="data.label" width="80" />
        </template>
      </Column>
      <Column field="label" header="Label" :sortable="true">
        <template #body="{ data }">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <img :src="data.img_url" :alt="data.label" width="40" style="border-radius: 4px;" />
            <span style="font-weight: 500;">{{ data.label }}</span>
          </div>
        </template>
      </Column>
      <Column field="curr_rating" header="Current Rating" :sortable="true">
        <template #body="{ data }">
          <div v-if="data.curr_rating !== null" style="display: flex; align-items: center; gap: 0.5rem;">
            <span :style="{ fontWeight: 'bold', color: getRatingColor(data.curr_rating), fontSize: '1.1rem' }">
              {{ data.curr_rating }}
            </span>
            <div class="rating-bar" :style="{ width: data.curr_rating * 10 + '%', backgroundColor: getRatingColor(data.curr_rating) }"></div>
          </div>
          <span v-else style="color: var(--text-color-secondary)">Not ranked yet</span>
        </template>
      </Column>
      <Column field="comparisons_count" header="Comparisons" :sortable="true">
        <template #body="{ data }">
          <span :style="{
            color: data.comparisons_count > 0 ? 'var(--primary-color)' : 'var(--text-color-secondary)',
            fontWeight: data.comparisons_count > 10 ? 'bold' : 'normal'
          }">
            {{ data.comparisons_count || 0 }}
          </span>
        </template>
      </Column>
      <Column field="stderr" header="Uncertainty" :sortable="true">
        <template #body="{ data }">
          <div v-if="data.stderr !== undefined && data.stderr > 0" style="display: flex; align-items: center; gap: 0.5rem;">
            <span :style="{ color: getUncertaintyColor(data.stderr) }">
              {{ data.stderr.toFixed(2) }}
            </span>
            <i
              v-if="data.stderr > 1.5"
              class="pi pi-exclamation-circle"
              :style="{ color: getUncertaintyColor(data.stderr) }"
              v-tooltip.top="'High uncertainty - needs more comparisons'"
            ></i>
          </div>
          <span v-else style="color: var(--text-color-secondary)">-</span>
        </template>
      </Column>
      <Column field="ability" header="Ability Score" :sortable="true">
        <template #body="{ data }">
          <code v-if="data.ability !== null" style="font-size: 0.9rem; color: var(--primary-color)">
            {{ data.ability }}
          </code>
          <span v-else style="color: var(--text-color-secondary)">-</span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
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

const searchQuery = ref("");
const filterBy = ref("all");

const filterOptions = [
  { label: "All Items", value: "all" },
  { label: "High Uncertainty", value: "high_uncertainty" },
  { label: "Well Ranked", value: "well_ranked" },
  { label: "Top Rated", value: "top_rated" },
  { label: "Needs Comparisons", value: "needs_comparisons" },
];

const filteredItems = computed(() => {
  let filtered = items.value;

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(item =>
      item.label.toLowerCase().includes(query)
    );
  }

  // Category filter
  switch (filterBy.value) {
    case "high_uncertainty":
      filtered = filtered.filter(item => item.stderr > 1.0);
      break;
    case "well_ranked":
      filtered = filtered.filter(item => item.stderr !== undefined && item.stderr <= 0.5);
      break;
    case "top_rated":
      filtered = filtered.filter(item => item.curr_rating !== null && item.curr_rating >= 7);
      break;
    case "needs_comparisons":
      filtered = filtered.filter(item => item.comparisons_count < 5);
      break;
  }

  return filtered;
});

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

function getCompletionPercentage() {
  if (!ranking.value || ranking.value.item_count < 2) return 0;
  const totalPossible = (ranking.value.item_count * (ranking.value.item_count - 1)) / 2;
  return Math.min(100, ((ranking.value.comp_count / totalPossible) * 100).toFixed(1));
}

function getRatingColor(rating) {
  if (rating < 3) return "#ef4444";
  if (rating < 5) return "#f59e0b";
  if (rating < 7) return "#eab308";
  if (rating < 9) return "#84cc16";
  return "#22c55e";
}

function getUncertaintyColor(stderr) {
  if (stderr > 2) return "#ef4444";
  if (stderr > 1) return "#f59e0b";
  if (stderr > 0.5) return "#eab308";
  return "#22c55e";
}

function exportToCSV() {
  if (!items.value || items.value.length === 0) return;

  const headers = ["Rank", "Label", "Current Rating", "Ability Score", "Uncertainty", "Comparisons", "Initial Rating"];
  const rows = items.value
    .filter(item => item.curr_rating !== null)
    .sort((a, b) => (b.curr_rating || 0) - (a.curr_rating || 0))
    .map((item, index) => [
      index + 1,
      `"${item.label.replace(/"/g, '""')}"`,
      item.curr_rating || "",
      item.ability || "",
      item.stderr || "",
      item.comparisons_count || 0,
      item.init_rating || "",
    ]);

  const csv = [
    headers.join(","),
    ...rows.map(row => row.join(","))
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${ranking.value?.name || 'ranking'}_export.csv`);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  toast.add({
    severity: "success",
    summary: "Exported",
    detail: `Exported ${rows.length} items to CSV`,
    life: 3000,
  });
}

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

.ranking-stats {
  margin: 0.5rem 0 0 0;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.ranking-stats .separator {
  margin: 0 0.5rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  gap: 1rem;
}

.empty-state h3 {
  margin: 0;
  color: var(--text-color);
}

.empty-state p {
  margin: 0;
  color: var(--text-color-secondary);
}

.search-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.rating-bar {
  height: 8px;
  border-radius: 4px;
  transition: width 0.3s ease;
  max-width: 100px;
}
</style>
