import { ref } from "vue";

/**
 * Composable for managing async actions with loading state.
 * Prevents spam clicking and provides automatic loading indicators.
 * Ideal for button actions, form submissions, and API calls.
 *
 * @example
 * ```js
 * const saveAction = useAsyncAction(
 *   async () => await REST.post('/items', data),
 *   {
 *     onSuccess: () => console.log('Saved!'),
 *     onError: (err) => console.error(err)
 *   }
 * );
 *
 * // In template:
 * <Button @click="saveAction.execute()" :loading="saveAction.isLoading.value" />
 * ```
 *
 * @param {Function} asyncFn - The async function to execute
 * @param {Object} options - Configuration options
 * @param {Function} options.onSuccess - Callback on success
 * @param {Function} options.onError - Callback on error
 * @param {Function} options.onFinally - Callback that always runs
 * @returns {Object} Action handler and state
 * @returns {Function} return.execute - Execute the async action
 * @returns {Function} return.reset - Reset state to initial
 * @returns {import('vue').Ref<boolean>} return.isLoading - Loading state
 * @returns {import('vue').Ref<Error|null>} return.error - Error state
 * @returns {import('vue').Ref<any>} return.data - Result data
 */
export function useAsyncAction(
  asyncFn,
  { onSuccess = null, onError = null, onFinally = null } = {}
) {
  const isLoading = ref(false);
  const error = ref(null);
  const data = ref(null);

  /**
   * Executes the async action with loading state management
   * @param {...any} args - Arguments to pass to the async function
   * @returns {Promise<any>} Result of the async function
   */
  async function execute(...args) {
    // Prevent execution if already loading
    if (isLoading.value) {
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const result = await asyncFn(...args);
      data.value = result;

      if (onSuccess) {
        onSuccess(result);
      }

      return result;
    } catch (err) {
      error.value = err;

      if (onError) {
        onError(err);
      }

      throw err; // Re-throw to allow caller to handle if needed
    } finally {
      isLoading.value = false;

      if (onFinally) {
        onFinally();
      }
    }
  }

  /**
   * Resets the action state
   */
  function reset() {
    isLoading.value = false;
    error.value = null;
    data.value = null;
  }

  return {
    execute,
    reset,
    isLoading,
    error,
    data,
  };
}

/**
 * Creates a debounced async action (useful for search inputs, autocomplete, etc.).
 * Delays execution until user stops typing for specified duration.
 *
 * @example
 * ```js
 * const searchAction = useDebouncedAsyncAction(
 *   async (query) => await REST.get(`/search?q=${query}`),
 *   300
 * );
 *
 * // In input handler:
 * searchAction.execute(searchQuery.value);
 * ```
 *
 * @param {Function} asyncFn - The async function to execute
 * @param {number} delay - Debounce delay in milliseconds (default: 300)
 * @param {Object} options - Same options as useAsyncAction
 * @returns {Object} Action handler and state (same as useAsyncAction)
 */
export function useDebouncedAsyncAction(asyncFn, delay = 300, options = {}) {
  const action = useAsyncAction(asyncFn, options);
  let timeoutId = null;

  function debouncedExecute(...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      action.execute(...args);
      timeoutId = null;
    }, delay);
  }

  return {
    ...action,
    execute: debouncedExecute,
  };
}

/**
 * Creates multiple async actions with a convenient object API.
 * Factory function for managing several actions simultaneously with clean namespacing.
 *
 * @example
 * ```js
 * const actions = useAsyncActions({
 *   save: async () => await REST.post('/items', data),
 *   delete: async (id) => await REST.delete(`/items/${id}`),
 *   refresh: async () => await REST.get('/items')
 * });
 *
 * await actions.save.execute();
 * await actions.delete.execute(itemId);
 *
 * // In template:
 * <Button @click="actions.save.execute()" :loading="actions.save.isLoading.value" />
 * <Button @click="actions.delete.execute(id)" :loading="actions.delete.isLoading.value" />
 * ```
 *
 * @param {Object} actionsMap - Object mapping action names to async functions
 * @returns {Object} Object with action handlers keyed by name
 */
export function useAsyncActions(actionsMap) {
  const actions = {};
  for (const [name, fn] of Object.entries(actionsMap)) {
    actions[name] = useAsyncAction(fn);
  }
  return actions;
}
