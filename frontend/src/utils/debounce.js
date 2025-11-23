/**
 * Creates a debounced version of a function that delays invoking until after
 * wait milliseconds have elapsed since the last time it was invoked.
 *
 * @param {Function} fn - The function to debounce
 * @param {number} delay - The delay in milliseconds
 * @returns {Function} The debounced function
 */
export function debounce(fn, delay) {
  let timeoutId = null;

  return function debounced(...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      fn.apply(this, args);
      timeoutId = null;
    }, delay);
  };
}

/**
 * Vue 3 composable for creating debounced refs
 * Usage: const debouncedSearch = useDebouncedRef(searchQuery, 300);
 *
 * @param {import('vue').Ref} source - The source ref to watch
 * @param {number} delay - The delay in milliseconds
 * @returns {import('vue').Ref} The debounced ref
 */
export function useDebouncedRef(source, delay) {
  const { ref, watch } = require('vue');
  const debounced = ref(source.value);

  watch(source, debounce((value) => {
    debounced.value = value;
  }, delay));

  return debounced;
}
