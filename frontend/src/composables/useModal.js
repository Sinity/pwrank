import { ref } from "vue";

/**
 * Composable for managing modal/dialog state
 * Reduces boilerplate for modal open/close logic
 *
 * @param {boolean} initialState - Initial visibility state (default: false)
 * @returns {Object} Modal state and control methods
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
 * Creates multiple modals with a convenient object API
 * @param {string[]} modalNames - Array of modal names
 * @returns {Object} Object with modal controls keyed by name
 *
 * @example
 * const modals = useModals(['add', 'edit', 'delete'])
 * modals.add.open()
 * modals.edit.isOpen.value = true
 */
export function useModals(modalNames) {
  const modals = {};
  for (const name of modalNames) {
    modals[name] = useModal();
  }
  return modals;
}
