<template>
  <div class="rankings-page">
    <Dialog
      header="Create ranking"
      v-model:visible="displayCreateRankingModal"
      :style="{ width: '50vw' }"
      :modal="true"
    >
      <div class="p-fluid">
        <div class="p-field p-grid">
          <div class="p-col-12 p-md-10">
            <InputText
              v-model="name"
              id="name"
              type="text"
              placeholder="Name"
            />
          </div>
        </div>
        <div class="p-field p-grid">
          <div class="p-col-12 p-md-10">
            <Dropdown
              v-model="datasource"
              :options="datasourceOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Datasource"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="Submit"
          icon="pi pi-check"
          @click="createRanking"
          :loading="saving"
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
      <div class="p-formgroup-inline">
        <div class="p-field">
          <label for="edit-name" class="p-sr-only">Name</label>
          <InputText
            v-model="name"
            id="edit-name"
            type="text"
            placeholder="Name"
          />
        </div>
      </div>

      <template #footer>
        <Button
          label="Submit"
          icon="pi pi-check"
          @click="modifyRanking"
          :loading="saving"
          autofocus
        />
      </template>
    </Dialog>

    <div class="card">
      <DataView
        :value="rankings"
        :layout="layout"
        :paginator="true"
        :rows="9"
        :sortOrder="sortOrder"
        :sortField="sortField"
        :loading="loading"
      >
        <template #header>
          <div class="p-grid p-nogutter">
            <div class="p-col-12 p-md-3" style="text-align: left">
              <Dropdown
                v-model="sortKey"
                :options="sortOptions"
                optionLabel="label"
                placeholder="Sort by"
                @change="onSortChange"
              />
            </div>
            <div class="p-col-12 p-md-6" style="text-align: center">
              <Button
                icon="pi pi-plus"
                label="Create new"
                @click="showCreateRanking"
              />
            </div>
            <div class="p-col-12 p-md-3" style="text-align: right">
              <DataViewLayoutOptions v-model="layout" />
            </div>
          </div>
        </template>

        <template #list="{ data }">
          <div class="p-col-12">
            <div class="product-list-item">
              <img
                :src="`${baseURL}${data.datasource}.png`"
                :alt="data.datasource"
              />
              <div class="product-list-detail">
                <i class="pi pi-tag product-category-icon"></i>
                <span class="product-category">{{ data.datasource }}</span>
                <div class="product-name">{{ data.name }}</div>
                <div class="product-description">{{ data.id }}</div>
                <div>
                  <span :class="badgeClass(data.datasource)"
                    >{{ data.item_count }} items</span
                  >
                </div>
              </div>
              <div class="product-list-action">
                <Button
                  icon="pi pi-bars"
                  label="Open"
                  @click="
                    router.push({ name: 'Ranking', params: { id: data.id } })
                  "
                />
                <Button
                  class="p-button-warning"
                  icon="pi pi-pencil"
                  label="Edit"
                  @click="showModifyRanking(data)"
                />
                <Button
                  class="p-button-danger"
                  icon="pi pi-trash"
                  label="Delete"
                  @click="deleteRanking(data.id)"
                />
              </div>
            </div>
          </div>
        </template>

        <template #grid="{ data }">
          <div class="p-col-12 p-md-4">
            <div class="product-grid-item card">
              <div class="product-grid-item-top">
                <div>
                  <i class="pi pi-tag product-category-icon"></i>
                  <span class="product-category">{{ data.datasource }}</span>
                </div>
                <span :class="badgeClass(data.datasource)"
                  >{{ data.item_count }} items</span
                >
              </div>
              <div class="product-grid-item-content">
                <img
                  :src="`${baseURL}${data.datasource}.png`"
                  :alt="data.datasource"
                />
                <div class="product-name">{{ data.name }}</div>
                <div class="product-description">{{ data.id }}</div>
              </div>
              <div class="product-grid-item-bottom">
                <Button
                  icon="pi pi-bars"
                  @click="
                    router.push({ name: 'Ranking', params: { id: data.id } })
                  "
                />
                <Button
                  class="p-button-warning"
                  icon="pi pi-pencil"
                  @click="showModifyRanking(data)"
                />
                <Button
                  class="p-button-danger"
                  icon="pi pi-trash"
                  @click="deleteRanking(data.id)"
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
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";

import { REST, HttpError } from "../rest";

const router = useRouter();
const toast = useToast();

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

const baseURL = process.env.BASE_URL || "/";

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
      life: 4000,
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
      life: 3000,
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
      life: 4000,
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
      life: 3000,
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
      life: 4000,
    });
  } finally {
    saving.value = false;
  }
}

async function deleteRanking(id) {
  try {
    const data = await REST.del(`/ranking/${id}`);
    toast.add({
      severity: "success",
      summary: "Ranking deleted",
      detail: data.message ?? "",
      life: 3000,
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
      life: 4000,
    });
  }
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
</style>
