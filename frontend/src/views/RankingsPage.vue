<template>
  <div class="rankings-page">
    <Toast />
    <ConfirmDialog />
    <Dialog
      header="Create ranking"
      v-model:visible="displayCreateRankingModal"
      :style="{ width: '50vw' }"
      :modal="true"
    >
      <div class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="name">Ranking Name *</label>
          <InputText
            v-model="name"
            id="name"
            type="text"
            placeholder="Enter ranking name"
            aria-required="true"
            aria-describedby="name_help"
          />
          <small id="name_help" class="help-text">A descriptive name for this ranking</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="datasource">Data Source *</label>
          <Dropdown
            v-model="datasource"
            id="datasource"
            :options="datasourceOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Select data source"
            aria-required="true"
            aria-describedby="datasource_help"
          />
          <small id="datasource_help" class="help-text">Where to sync items from (AniList for anime, Steam for games)</small>
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="displayCreateRankingModal = false"
        />
        <Button
          label="Create"
          icon="pi pi-check"
          @click="createRanking"
          :loading="saving"
          :disabled="!isCreateFormValid"
          autofocus
        />
      </template>
    </Dialog>

    <Dialog
      header="Modify ranking"
      v-model:visible="displayModifyRankingModal"
      :style="{ width: '50vw' }"
      :modal="true"
    >
      <div class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="edit-name">Ranking Name *</label>
          <InputText
            v-model="name"
            id="edit-name"
            type="text"
            placeholder="Enter new ranking name"
            maxlength="255"
            aria-required="true"
          />
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="displayModifyRankingModal = false"
        />
        <Button
          label="Save"
          icon="pi pi-check"
          @click="modifyRanking"
          :loading="saving"
          :disabled="!name.trim()"
          autofocus
        />
      </template>
    </Dialog>

    <div class="card">
      <!-- Loading Skeleton -->
      <div v-if="loading" class="skeleton-grid">
        <div v-for="i in 6" :key="i" class="skeleton-card">
          <Skeleton height="200px" class="mb-3" />
          <Skeleton height="1.5rem" width="70%" class="mb-2" />
          <Skeleton height="1rem" width="50%" />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && rankings.length === 0" class="empty-state">
        <i class="pi pi-star" style="font-size: 4rem; color: var(--text-color-secondary)"></i>
        <h2>No Rankings Yet</h2>
        <p>Create your first ranking to start comparing items!</p>
        <Button
          icon="pi pi-plus"
          label="Create Your First Ranking"
          class="p-button-lg p-button-success"
          @click="showCreateRanking"
        />
      </div>

      <DataView
        v-else-if="rankings.length > 0"
        :value="rankings"
        :layout="layout"
        :paginator="true"
        :rows="9"
        :sortOrder="sortOrder"
        :sortField="sortField"
      >
        <template #header>
          <div class="flex flex-wrap align-items-center justify-content-between gap-3">
            <Dropdown
              v-model="sortKey"
              :options="sortOptions"
              optionLabel="label"
              placeholder="Sort by"
              @change="onSortChange"
            />
            <Button
              icon="pi pi-plus"
              label="Create new"
              @click="showCreateRanking"
              v-tooltip.top="'Create a new ranking'"
            />
            <DataViewLayoutOptions v-model="layout" />
          </div>
        </template>

        <template #list="{ data }">
          <div class="col-12">
            <div class="product-list-item">
              <img
                :src="`${baseURL}${data.datasource}.png`"
                :alt="`${data.datasource} logo`"
                @error="handleImageError"
              />
              <div class="product-list-detail">
                <i class="pi pi-tag product-category-icon"></i>
                <span class="product-category">{{ data.datasource }}</span>
                <div class="product-name">{{ data.name }}</div>
                <div class="product-description">
                  {{ data.item_count }} {{ data.item_count === 1 ? 'item' : 'items' }} •
                  {{ data.comp_count }} {{ data.comp_count === 1 ? 'comparison' : 'comparisons' }}
                </div>
                <div class="ranking-meta">
                  <span :class="badgeClass(data.datasource)">
                    {{ data.item_count }} items
                  </span>
                  <span class="comparison-badge">
                    {{ data.comp_count }} comparisons
                  </span>
                </div>
              </div>
              <div class="product-list-action">
                <Button
                  icon="pi pi-bars"
                  label="Open"
                  @click="
                    router.push({ name: 'Ranking', params: { id: data.id } })
                  "
                  v-tooltip.top="'View and manage ranking items'"
                />
                <Button
                  class="p-button-warning"
                  icon="pi pi-pencil"
                  label="Edit"
                  @click="showModifyRanking(data)"
                  v-tooltip.top="'Rename this ranking'"
                />
                <Button
                  class="p-button-danger"
                  icon="pi pi-trash"
                  label="Delete"
                  @click="deleteRanking(data.id)"
                  v-tooltip.top="'Delete this ranking permanently'"
                />
              </div>
            </div>
          </div>
        </template>

        <template #grid="{ data }">
          <div class="col-12 md:col-4">
            <div class="product-grid-item card">
              <div class="product-grid-item-top">
                <div>
                  <i class="pi pi-tag product-category-icon"></i>
                  <span class="product-category">{{ data.datasource }}</span>
                </div>
                <div class="badges">
                  <span :class="badgeClass(data.datasource)">
                    {{ data.item_count }} items
                  </span>
                  <span class="comparison-badge">
                    {{ data.comp_count }}
                  </span>
                </div>
              </div>
              <div class="product-grid-item-content">
                <img
                  :src="`${baseURL}${data.datasource}.png`"
                  :alt="`${data.datasource} logo`"
                  @error="handleImageError"
                />
                <div class="product-name">{{ data.name }}</div>
                <div class="product-description">
                  {{ data.item_count }} {{ data.item_count === 1 ? 'item' : 'items' }}
                </div>
              </div>
              <div class="product-grid-item-bottom">
                <Button
                  icon="pi pi-bars"
                  @click="
                    router.push({ name: 'Ranking', params: { id: data.id } })
                  "
                  v-tooltip.top="'Open ranking'"
                />
                <Button
                  class="p-button-warning"
                  icon="pi pi-pencil"
                  @click="showModifyRanking(data)"
                  v-tooltip.top="'Rename'"
                />
                <Button
                  class="p-button-danger"
                  icon="pi pi-trash"
                  @click="deleteRanking(data.id)"
                  v-tooltip.top="'Delete'"
                />
              </div>
            </div>
          </div>
        </template>
      </DataView>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";

import { REST, HttpError } from "../rest";
import { FALLBACK_IMAGE_SVG, TOAST_DURATION_NORMAL, TOAST_DURATION_LONG } from "../constants";

const router = useRouter();
const toast = useToast();
const confirm = useConfirm();

const handleImageError = (event) => {
  event.target.src = FALLBACK_IMAGE_SVG;
};

const rankings = ref([]);
const loading = ref(false);
const saving = ref(false);

const displayCreateRankingModal = ref(false);
const displayModifyRankingModal = ref(false);
const rankingId = ref("");
const name = ref("");
const datasource = ref("steam");

const datasourceOptions = [
  { label: "Steam", value: "steam" },
  { label: "Anilist", value: "anilist" },
];

const layout = ref("grid");
const sortKey = ref(null);
const sortOrder = ref(null);
const sortField = ref(null);

const sortOptions = [
  { label: "Item count High to Low", value: "!item_count" },
  { label: "Item count Low to High", value: "item_count" },
  { label: "Name High to Low", value: "!name" },
  { label: "Name Low to High", value: "name" },
  { label: "ID High to Low", value: "!id" },
  { label: "ID Low to High", value: "id" },
];

const baseURL = import.meta.env.BASE_URL || "/";

const isCreateFormValid = computed(() => name.value.trim().length > 0 && datasource.value);

function badgeClass(source) {
  return `product-badge status-${source.toLowerCase()}`;
}

async function refreshRankings() {
  loading.value = true;
  try {
    const data = await REST.get("/ranking");
    rankings.value = data.rankings ?? [];
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to load rankings",
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

function showCreateRanking() {
  name.value = "";
  datasource.value = "steam";
  displayCreateRankingModal.value = true;
}

function showModifyRanking(ranking) {
  rankingId.value = ranking.id;
  name.value = ranking.name;
  displayModifyRankingModal.value = true;
}

async function createRanking() {
  saving.value = true;
  try {
    const payload = {
      name: name.value,
      source: datasource.value,
    };
    const data = await REST.post("/ranking", payload);
    toast.add({
      severity: "success",
      summary: "Ranking created",
      detail: data.message ?? "",
      life: TOAST_DURATION_NORMAL,
    });
    displayCreateRankingModal.value = false;
    await refreshRankings();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to create ranking",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: TOAST_DURATION_LONG,
    });
  } finally {
    saving.value = false;
  }
}

async function modifyRanking() {
  saving.value = true;
  try {
    const data = await REST.put(`/ranking/${rankingId.value}`, {
      name: name.value,
    });
    toast.add({
      severity: "success",
      summary: "Ranking updated",
      detail: data.message ?? "",
      life: TOAST_DURATION_NORMAL,
    });
    displayModifyRankingModal.value = false;
    await refreshRankings();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Failed to update ranking",
      detail:
        error instanceof HttpError
          ? error.payload?.message || "Unexpected backend response."
          : "Unable to reach the backend.",
      life: TOAST_DURATION_LONG,
    });
  } finally {
    saving.value = false;
  }
}

async function deleteRanking(id) {
  confirm.require({
    message: "Are you sure you want to delete this ranking? This action cannot be undone.",
    header: "Confirm Deletion",
    icon: "pi pi-exclamation-triangle",
    acceptClass: "p-button-danger",
    accept: async () => {
      try {
        const data = await REST.del(`/ranking/${id}`);
        toast.add({
          severity: "success",
          summary: "Ranking deleted",
          detail: data.message ?? "",
          life: TOAST_DURATION_NORMAL,
        });
        await refreshRankings();
      } catch (error) {
        toast.add({
          severity: "error",
          summary: "Failed to delete ranking",
          detail:
            error instanceof HttpError
              ? error.payload?.message || "Unexpected backend response."
              : "Unable to reach the backend.",
          life: TOAST_DURATION_LONG,
        });
      }
    },
  });
}

function onSortChange(event) {
  const value = event.value.value;
  const sortValue = event.value;

  if (value.indexOf("!") === 0) {
    sortOrder.value = -1;
    sortField.value = value.substring(1);
    sortKey.value = sortValue;
  } else {
    sortOrder.value = 1;
    sortField.value = value;
    sortKey.value = sortValue;
  }
}

onMounted(refreshRankings);
</script>

<style scoped>
.rankings-page .p-button {
  margin: 0.3rem 0.5rem;
  min-width: 10rem;
}

.card {
  padding: 2rem;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14),
    0 1px 3px 0 rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  margin-bottom: 2rem;
}

.p-dropdown {
  width: 18rem;
  font-weight: normal;
}

.product-name {
  font-size: 2rem;
  font-weight: 700;
}

.product-description {
  margin: 0 0 1rem 0;
}

.product-category-icon {
  vertical-align: middle;
  margin-right: 0.5rem;
}

.product-category {
  font-weight: 600;
  vertical-align: middle;
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

.empty-state h2 {
  margin: 0;
  color: var(--text-color);
}

.empty-state p {
  margin: 0;
  color: var(--text-color-secondary);
  max-width: 500px;
}

.ranking-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.comparison-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background-color: var(--primary-color);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
}

.badges {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-end;
}

::v-deep(.product-list-item) {
  display: flex;
  align-items: center;
  padding: 1rem;
  width: 100%;
  gap: 1.5rem;

  img {
    width: 50px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
  }

  .product-list-detail {
    flex: 1 1 0;
  }

  .product-list-action {
    display: flex;
    flex-direction: column;
  }

  .p-button {
    margin-bottom: 0.5rem;
  }
}

::v-deep(.product-grid-item) {
  margin: 0.5rem;
  border: 1px solid #dee2e6;

  .product-grid-item-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .product-grid-item-bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  img {
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
    margin: 2rem 0;
  }

  .product-grid-item-content {
    text-align: center;
  }
}

@media screen and (max-width: 576px) {
  .product-list-item {
    flex-direction: column;
    align-items: center;

    img {
      margin: 2rem 0;
    }

    .product-list-detail {
      text-align: center;
    }

    .product-list-action {
      margin-top: 2rem;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      width: 100%;
    }
  }
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

.skeleton-card {
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

.help-text {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}
</style>
