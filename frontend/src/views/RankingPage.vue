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
          v-if="selectedItems.length > 0"
          icon="pi pi-trash"
          :label="`Delete Selected (${selectedItems.length})`"
          class="p-button-danger"
          @click="openBulkDeleteConfirmDialog"
        />
        <Button
          icon="pi pi-download"
          label="Export CSV"
          class="p-button-secondary"
          @click="exportToCSV"
          :disabled="!ranking || items.length === 0"
          v-tooltip.top="items.length === 0 ? 'No items to export' : 'Export ranking to CSV file'"
        />
        <Button
          icon="pi pi-plus"
          label="Add Item"
          class="p-button-secondary"
          @click="openAddItemDialog"
          :disabled="!ranking"
          v-tooltip.top="'Add a new item manually'"
        />
        <Button
          icon="pi pi-sync"
          label="Sync items"
          @click="openSyncDialog"
          :disabled="!ranking"
          v-tooltip.top="'Import items from external source'"
        />
        <Button
          icon="pi pi-arrow-right"
          label="Compare"
          class="p-button-success"
          @click="router.push({ name: 'Comparing', params: { id: rankingId } })"
          :disabled="!ranking || items.length < 2"
          v-tooltip.top="items.length < 2 ? 'Need at least 2 items to compare' : 'Start comparing items'"
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

    <!-- Add Item Dialog -->
    <Dialog
      v-model:visible="displayAddItemModal"
      header="Add New Item"
      :style="{ width: '50vw' }"
      :modal="true"
    >
      <div class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="item_label">Label *</label>
          <InputText
            id="item_label"
            v-model="itemForm.label"
            type="text"
            placeholder="Enter item name (max 200 characters)"
            maxlength="200"
            aria-required="true"
            aria-describedby="item_label_help"
          />
          <small id="item_label_help" class="help-text">The display name for this item</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="item_img_url">Image URL (optional)</label>
          <InputText
            id="item_img_url"
            v-model="itemForm.img_url"
            type="text"
            placeholder="https://example.com/image.jpg"
            maxlength="500"
            aria-describedby="item_img_url_help"
          />
          <small id="item_img_url_help" class="help-text">URL to an image representing this item</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="item_init_rating">Initial Rating (0-10)</label>
          <InputNumber
            id="item_init_rating"
            v-model="itemForm.init_rating"
            :min="0"
            :max="10"
            :step="1"
            aria-describedby="item_init_rating_help"
          />
          <small id="item_init_rating_help" class="help-text">Starting rating before comparisons (0 = lowest, 10 = highest)</small>
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="displayAddItemModal = false"
        />
        <Button
          label="Add"
          icon="pi pi-check"
          @click="addItem"
          :loading="submitting"
          :disabled="!isAddItemFormValid"
          autofocus
        />
      </template>
    </Dialog>

    <!-- Edit Item Dialog -->
    <Dialog
      v-model:visible="displayEditItemModal"
      header="Edit Item"
      :style="{ width: '50vw' }"
      :modal="true"
    >
      <div class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="edit_item_label">Label *</label>
          <InputText
            id="edit_item_label"
            v-model="editItemForm.label"
            type="text"
            placeholder="Enter item name (max 200 characters)"
            maxlength="200"
            aria-required="true"
            aria-describedby="edit_item_label_help"
          />
          <small id="edit_item_label_help" class="help-text">The display name for this item</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="edit_item_img_url">Image URL (optional)</label>
          <InputText
            id="edit_item_img_url"
            v-model="editItemForm.img_url"
            type="text"
            placeholder="https://example.com/image.jpg"
            maxlength="500"
            aria-describedby="edit_item_img_url_help"
          />
          <small id="edit_item_img_url_help" class="help-text">URL to an image representing this item</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="edit_item_init_rating">Initial Rating (0-10)</label>
          <InputNumber
            id="edit_item_init_rating"
            v-model="editItemForm.init_rating"
            :min="0"
            :max="10"
            :step="1"
            aria-describedby="edit_item_init_rating_help"
          />
          <small id="edit_item_init_rating_help" class="help-text">Starting rating before comparisons (0 = lowest, 10 = highest)</small>
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="displayEditItemModal = false"
        />
        <Button
          label="Save"
          icon="pi pi-check"
          @click="updateItem"
          :loading="submitting"
          :disabled="!isEditItemFormValid"
          autofocus
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog
      v-model:visible="displayDeleteConfirmModal"
      header="Confirm Delete"
      :style="{ width: '30vw' }"
      :modal="true"
    >
      <p>Are you sure you want to delete "<strong>{{ itemToDelete?.label }}</strong>"?</p>
      <p style="color: var(--text-color-secondary); font-size: 0.9rem;">
        This will also delete all comparisons involving this item.
      </p>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="displayDeleteConfirmModal = false"
        />
        <Button
          label="Delete"
          icon="pi pi-trash"
          class="p-button-danger"
          @click="deleteItem"
          :loading="submitting"
          autofocus
        />
      </template>
    </Dialog>

    <!-- Bulk Delete Confirmation Dialog -->
    <Dialog
      v-model:visible="displayBulkDeleteConfirmModal"
      header="Confirm Bulk Delete"
      :style="{ width: '30vw' }"
      :modal="true"
    >
      <p>Are you sure you want to delete <strong>{{ selectedItems.length }}</strong> selected items?</p>
      <p style="color: var(--text-color-secondary); font-size: 0.9rem;">
        This will also delete all comparisons involving these items. This action cannot be undone.
      </p>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="displayBulkDeleteConfirmModal = false"
        />
        <Button
          label="Delete All"
          icon="pi pi-trash"
          class="p-button-danger"
          @click="bulkDeleteItems"
          :loading="submitting"
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

    <!-- Loading Skeleton -->
    <div v-if="loading && !ranking" class="skeleton-container">
      <Skeleton height="3rem" class="mb-2" />
      <Skeleton height="2rem" width="60%" class="mb-4" />
      <div class="skeleton-table">
        <Skeleton v-for="i in 5" :key="i" height="4rem" class="mb-2" />
      </div>
    </div>

    <!-- Search and Filter -->
    <div v-if="!loading && items.length > 0" class="search-controls">
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
      v-if="!loading && items.length > 0"
      :value="filteredItems"
      v-model:selection="selectedItems"
      :paginator="filteredItems.length > 20"
      :rows="20"
      sortField="curr_rating"
      :sortOrder="-1"
      stripedRows
      dataKey="id"
    >
      <Column selectionMode="multiple" headerStyle="width: 3rem" :exportable="false"></Column>
      <Column field="img_url" header="Image">
        <template #body="{ data }">
          <img
            :src="data.img_url || FALLBACK_IMAGE"
            :alt="data.label"
            width="80"
            @error="handleImageError"
          />
        </template>
      </Column>
      <Column field="label" header="Label" :sortable="true">
        <template #body="{ data }">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <img
              :src="data.img_url || FALLBACK_IMAGE"
              :alt="data.label"
              width="40"
              style="border-radius: 4px;"
              @error="handleImageError"
            />
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
      <Column header="Actions" :exportable="false" style="width: 150px">
        <template #body="{ data }">
          <div style="display: flex; gap: 0.5rem;">
            <Button
              icon="pi pi-pencil"
              class="p-button-sm p-button-text"
              @click="openEditItemDialog(data)"
              v-tooltip.top="'Edit item'"
            />
            <Button
              icon="pi pi-trash"
              class="p-button-sm p-button-text p-button-danger"
              @click="openDeleteConfirmDialog(data)"
              v-tooltip.top="'Delete item'"
            />
          </div>
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

// Fallback image for broken or missing images
const FALLBACK_IMAGE = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2224%22%3ENo Image%3C/text%3E%3C/svg%3E';

const handleImageError = (event) => {
  event.target.src = FALLBACK_IMAGE;
};

const ranking = ref(null);
const items = ref([]);
const rankingId = ref(route.params.id);
const loading = ref(false);
const syncing = ref(false);
const submitting = ref(false);
const selectedItems = ref([]);

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
  let filtered = items.value || [];

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(item =>
      item?.label?.toLowerCase().includes(query)
    );
  }

  // Category filter
  switch (filterBy.value) {
    case "high_uncertainty":
      filtered = filtered.filter(item => item.stderr != null && item.stderr > 1.0);
      break;
    case "well_ranked":
      filtered = filtered.filter(item => item.stderr != null && item.stderr <= 0.5);
      break;
    case "top_rated":
      filtered = filtered.filter(item => item.curr_rating != null && item.curr_rating >= 7);
      break;
    case "needs_comparisons":
      filtered = filtered.filter(item => (item.comparisons_count || 0) < 5);
      break;
  }

  return filtered;
});

const displaySyncModal = ref(false);
const steamId = ref("");
const anilistUsername = ref("");
const anilistStatuses = ref([]);

const displayAddItemModal = ref(false);
const displayEditItemModal = ref(false);
const displayDeleteConfirmModal = ref(false);
const displayBulkDeleteConfirmModal = ref(false);
const itemForm = ref({ label: "", img_url: "", init_rating: 5 });
const editItemForm = ref({ id: "", label: "", img_url: "", init_rating: 5 });
const itemToDelete = ref(null);

const anilistStatusOptions = [
  { label: "Current", value: "CURRENT" },
  { label: "Planning", value: "PLANNING" },
  { label: "Paused", value: "PAUSED" },
  { label: "Completed", value: "COMPLETED" },
  { label: "Dropped", value: "DROPPED" },
  { label: "Repeating", value: "REPEATING" },
];

const isAddItemFormValid = computed(() => itemForm.value.label.trim().length > 0);
const isEditItemFormValid = computed(() => editItemForm.value.label.trim().length > 0);

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
    .sort((a, b) => (b.curr_rating ?? 0) - (a.curr_rating ?? 0))
    .map((item, index) => [
      index + 1,
      `"${item.label.replace(/"/g, '""')}"`,
      item.curr_rating ?? "",
      item.ability ?? "",
      item.stderr ?? "",
      item.comparisons_count || 0,
      item.init_rating ?? "",
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

function openAddItemDialog() {
  itemForm.value = { label: "", img_url: "", init_rating: 5 };
  displayAddItemModal.value = true;
}

function openEditItemDialog(item) {
  editItemForm.value = {
    id: item.id,
    label: item.label,
    img_url: item.img_url || "",
    init_rating: typeof item.init_rating === "number" ? item.init_rating : 5,
  };
  displayEditItemModal.value = true;
}

function openDeleteConfirmDialog(item) {
  itemToDelete.value = item;
  displayDeleteConfirmModal.value = true;
}

async function addItem() {
  if (!itemForm.value.label.trim()) {
    toast.add({
      severity: "error",
      summary: "Validation Error",
      detail: "Item label is required.",
      life: 3000,
    });
    return;
  }

  submitting.value = true;
  try {
    await REST.post(`/ranking/${rankingId.value}/items`, {
      label: itemForm.value.label.trim(),
      img_url: itemForm.value.img_url.trim(),
      init_rating: itemForm.value.init_rating,
    });

    toast.add({
      severity: "success",
      summary: "Item Added",
      detail: `"${itemForm.value.label}" has been added to the ranking.`,
      life: 3000,
    });

    displayAddItemModal.value = false;
    await loadRanking();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to add item",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: 4000,
    });
  } finally {
    submitting.value = false;
  }
}

async function updateItem() {
  if (!editItemForm.value.label.trim()) {
    toast.add({
      severity: "error",
      summary: "Validation Error",
      detail: "Item label is required.",
      life: 3000,
    });
    return;
  }

  submitting.value = true;
  try {
    await REST.put(`/item/${editItemForm.value.id}`, {
      label: editItemForm.value.label.trim(),
      img_url: editItemForm.value.img_url.trim(),
      init_rating: editItemForm.value.init_rating,
    });

    toast.add({
      severity: "success",
      summary: "Item Updated",
      detail: `"${editItemForm.value.label}" has been updated.`,
      life: 3000,
    });

    displayEditItemModal.value = false;
    await loadRanking();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to update item",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: 4000,
    });
  } finally {
    submitting.value = false;
  }
}

async function deleteItem() {
  if (!itemToDelete.value) return;

  submitting.value = true;
  try {
    await REST.del(`/item/${itemToDelete.value.id}`);

    toast.add({
      severity: "success",
      summary: "Item Deleted",
      detail: `"${itemToDelete.value.label}" has been deleted.`,
      life: 3000,
    });

    displayDeleteConfirmModal.value = false;
    itemToDelete.value = null;
    await loadRanking();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to delete item",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: 4000,
    });
  } finally {
    submitting.value = false;
  }
}

function openBulkDeleteConfirmDialog() {
  displayBulkDeleteConfirmModal.value = true;
}

async function bulkDeleteItems() {
  if (selectedItems.value.length === 0) return;

  submitting.value = true;
  let successCount = 0;
  let errorCount = 0;

  try {
    // Delete all selected items
    for (const item of selectedItems.value) {
      try {
        await REST.del(`/item/${item.id}`);
        successCount++;
      } catch (error) {
        errorCount++;
        // Continue with other deletions despite failure
      }
    }

    // Show result toast
    if (successCount > 0) {
      toast.add({
        severity: errorCount > 0 ? "warn" : "success",
        summary: `Deleted ${successCount} items`,
        detail: errorCount > 0 ? `${errorCount} items failed to delete` : "",
        life: 3000,
      });
    }

    if (errorCount > 0 && successCount === 0) {
      toast.add({
        severity: "error",
        summary: "Failed to delete items",
        detail: "All deletions failed. Please try again.",
        life: 4000,
      });
    }

    displayBulkDeleteConfirmModal.value = false;
    selectedItems.value = [];
    await loadRanking();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to delete items",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: 4000,
    });
  } finally {
    submitting.value = false;
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

.skeleton-container {
  padding: 2rem 0;
}

.skeleton-table {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.help-text {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}
</style>
