import { ref } from "vue";

/**
 * Composable for managing modal/dialog state.
 * Reduces boilerplate for modal open/close logic and provides a clean API
 * for controlling dialog visibility.
 *
 * @example
 * ```js
 * const addModal = useModal();
 * addModal.open(); // Show modal
 * addModal.close(); // Hide modal
 *
 * // In template:
 * <Dialog v-model:visible="addModal.isOpen.value">...</Dialog>
 * ```
 *
 * @param {boolean} initialState - Initial visibility state (default: false)
 * @returns {Object} Modal state and control methods
 * @returns {import('vue').Ref<boolean>} return.isOpen - Reactive visibility state
 * @returns {Function} return.open - Open the modal
 * @returns {Function} return.close - Close the modal
 * @returns {Function} return.toggle - Toggle modal state
 * @returns {Function} return.openWith - Open with initialization function
 * @returns {Function} return.closeWith - Close with cleanup function
 */
export function useModal(initialState = false) {
  const isOpen = ref(initialState);

  /**
   * Opens the modal
   */
  function open() {
    isOpen.value = true;
  }

  /**
   * Closes the modal
   */
  function close() {
    isOpen.value = false;
  }

  /**
   * Toggles the modal state
   */
  function toggle() {
    isOpen.value = !isOpen.value;
  }

  /**
   * Opens modal with optional data initialization
   * @param {Function} initFn - Optional function to run before opening
   */
  function openWith(initFn) {
    if (initFn) {
      initFn();
    }
    open();
  }

  /**
   * Closes modal with optional cleanup
   * @param {Function} cleanupFn - Optional function to run before closing
   */
  function closeWith(cleanupFn) {
    if (cleanupFn) {
      cleanupFn();
    }
    close();
  }

  return {
    isOpen,
    open,
    close,
    toggle,
    openWith,
    closeWith,
  };
}

/**
 * Creates multiple modals with a convenient object API.
 * Factory function for managing several modals simultaneously with clean namespacing.
 *
 * @example
 * ```js
 * const modals = useModals(['add', 'edit', 'delete']);
 * modals.add.open();
 * modals.edit.isOpen.value = true;
 * modals.delete.close();
 *
 * // In template:
 * <Dialog v-model:visible="modals.add.isOpen.value">Add Item</Dialog>
 * <Dialog v-model:visible="modals.edit.isOpen.value">Edit Item</Dialog>
 * ```
 *
 * @param {string[]} modalNames - Array of modal names (e.g., ['add', 'edit', 'delete'])
 * @returns {Object} Object with modal controls keyed by name
 */
export function useModals(modalNames) {
  const modals = {};
  for (const name of modalNames) {
    modals[name] = useModal();
  }
  return modals;
}
