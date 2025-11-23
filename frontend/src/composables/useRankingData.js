import { ref, computed } from "vue";
import { REST } from "../rest";
import { useNotification } from "./useNotification";

/**
 * Composable for managing ranking data and item operations.
 * Centralizes all ranking-related state management and API calls.
 *
 * @example
 * ```js
 * const {
 *   ranking,
 *   items,
 *   filteredItems,
 *   loading,
 *   loadRanking,
 *   addItem,
 *   updateItem,
 *   deleteItem
 * } = useRankingData(rankingId);
 *
 * await loadRanking();
 * await addItem({ label: 'New Item', img_url: '', init_rating: 5 });
 * ```
 *
 * @param {import('vue').Ref<string>} rankingId - Reactive ranking ID
 * @returns {Object} Ranking data and operations
 */
export function useRankingData(rankingId) {
  const { notifySuccess, notifyError, notifyWarn } = useNotification();

  // State
  const ranking = ref(null);
  const items = ref([]);
  const loading = ref(false);
  const submitting = ref(false);

  // Search and filter state
  const searchQuery = ref("");
  const filterBy = ref("all");

  /**
   * Filter options for ranking items
   * @type {Array<{label: string, value: string}>}
   */
  const filterOptions = [
    { label: "All Items", value: "all" },
    { label: "High Uncertainty", value: "high_uncertainty" },
    { label: "Well Ranked", value: "well_ranked" },
    { label: "Top Rated", value: "top_rated" },
    { label: "Needs Comparisons", value: "needs_comparisons" },
  ];

  /**
   * Computed filtered items based on search query and filter selection
   */
  const filteredItems = computed(() => {
    let filtered = items.value || [];

    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      filtered = filtered.filter(item =>
        item?.label?.toLowerCase().includes(query)
      );
    }

    // Apply category filter
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

  /**
   * Calculate completion percentage based on total possible comparisons
   * @returns {number} Percentage complete (0-100)
   */
  function getCompletionPercentage() {
    if (!ranking.value || ranking.value.item_count < 2) return 0;
    const totalPossible = (ranking.value.item_count * (ranking.value.item_count - 1)) / 2;
    return Math.min(100, ((ranking.value.comp_count / totalPossible) * 100).toFixed(1));
  }

  /**
   * Load ranking data from API
   * @returns {Promise<void>}
   */
  async function loadRanking() {
    if (loading.value || !rankingId.value) return;

    loading.value = true;
    try {
      const data = await REST.get(`/ranking/${rankingId.value}`);
      ranking.value = data.ranking;
      items.value = data.ranking?.items ?? [];
    } catch (error) {
      notifyError(error, "Failed to load ranking");
    } finally {
      loading.value = false;
    }
  }

  /**
   * Add a new item to the ranking
   * @param {Object} itemData - Item data
   * @param {string} itemData.label - Item label
   * @param {string} itemData.img_url - Image URL
   * @param {number} itemData.init_rating - Initial rating
   * @returns {Promise<boolean>} True if successful
   */
  async function addItem(itemData) {
    if (submitting.value) return false;

    submitting.value = true;
    try {
      await REST.post(`/ranking/${rankingId.value}/items`, itemData);
      notifySuccess("Item Added", `"${itemData.label}" has been added to the ranking.`);
      await loadRanking();
      return true;
    } catch (error) {
      notifyError(error, "Failed to add item");
      return false;
    } finally {
      submitting.value = false;
    }
  }

  /**
   * Update an existing item
   * @param {string} itemId - Item ID
   * @param {Object} itemData - Updated item data
   * @returns {Promise<boolean>} True if successful
   */
  async function updateItem(itemId, itemData) {
    if (submitting.value) return false;

    submitting.value = true;
    try {
      await REST.put(`/item/${itemId}`, itemData);
      notifySuccess("Item Updated", `"${itemData.label}" has been updated.`);
      await loadRanking();
      return true;
    } catch (error) {
      notifyError(error, "Failed to update item");
      return false;
    } finally {
      submitting.value = false;
    }
  }

  /**
   * Delete an item from the ranking
   * @param {Object} item - Item to delete
   * @param {string} item.id - Item ID
   * @param {string} item.label - Item label (for notification)
   * @returns {Promise<boolean>} True if successful
   */
  async function deleteItem(item) {
    if (submitting.value || !item) return false;

    submitting.value = true;
    try {
      await REST.del(`/item/${item.id}`);
      notifySuccess("Item Deleted", `"${item.label}" has been deleted.`);
      await loadRanking();
      return true;
    } catch (error) {
      notifyError(error, "Failed to delete item");
      return false;
    } finally {
      submitting.value = false;
    }
  }

  /**
   * Bulk delete multiple items
   * @param {Array<Object>} itemsToDelete - Array of items to delete
   * @returns {Promise<{successCount: number, errorCount: number}>}
   */
  async function bulkDeleteItems(itemsToDelete) {
    if (submitting.value || itemsToDelete.length === 0) {
      return { successCount: 0, errorCount: 0 };
    }

    submitting.value = true;
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const item of itemsToDelete) {
        try {
          await REST.del(`/item/${item.id}`);
          successCount++;
        } catch (error) {
          errorCount++;
        }
      }

      // Show appropriate notification
      if (successCount > 0 && errorCount > 0) {
        notifyWarn(`Deleted ${successCount} items`, `${errorCount} items failed to delete`);
      } else if (successCount > 0) {
        notifySuccess(`Deleted ${successCount} items`);
      } else if (errorCount > 0) {
        notifyError("All deletions failed. Please try again.", "Failed to delete items");
      }

      await loadRanking();
      return { successCount, errorCount };
    } catch (error) {
      notifyError(error, "Failed to delete items");
      return { successCount, errorCount };
    } finally {
      submitting.value = false;
    }
  }

  /**
   * Sync items from external data source (Anilist, Steam, etc.)
   * @param {Object} syncData - Sync configuration
   * @param {string} syncData.anilist_username - Anilist username (if applicable)
   * @param {Array<string>} syncData.anilist_statuses - Anilist statuses (if applicable)
   * @param {string} syncData.steam_id - Steam ID (if applicable)
   * @returns {Promise<boolean>} True if successful
   */
  async function syncItems(syncData) {
    if (!ranking.value || submitting.value) return false;

    submitting.value = true;
    try {
      await REST.post(`/ranking/${rankingId.value}`, syncData);
      notifySuccess("Items synced");
      await loadRanking();
      return true;
    } catch (error) {
      notifyError(error, "Sync failed");
      return false;
    } finally {
      submitting.value = false;
    }
  }

  return {
    // State
    ranking,
    items,
    filteredItems,
    loading,
    submitting,
    searchQuery,
    filterBy,
    filterOptions,

    // Computed
    getCompletionPercentage,

    // Methods
    loadRanking,
    addItem,
    updateItem,
    deleteItem,
    bulkDeleteItems,
    syncItems,
  };
}
