import { computed } from "vue";
import { isValidEmail, isSafeImageUrl } from "../utils/validation";
import { MIN_PASSWORD_LENGTH, MAX_ITEM_LABEL_LENGTH } from "../constants";

/**
 * Composable for reusable form validation logic.
 * Provides validation helpers and computed validators to ensure consistent
 * validation patterns across the application.
 *
 * @example
 * ```js
 * const { isRequired, isPasswordValid, useEmailValidation } = useFormValidation();
 * const emailRef = ref("");
 * const isEmailValid = useEmailValidation(emailRef);
 *
 * if (isRequired(form.name) && isPasswordValid(form.password)) {
 *   // Submit form
 * }
 * ```
 *
 * @returns {Object} Validation helper methods and factories
 * @returns {Function} return.isRequired - Check if value is non-empty
 * @returns {Function} return.isLengthValid - Validate string length
 * @returns {Function} return.isPasswordValid - Validate password requirements
 * @returns {Function} return.isLabelValid - Validate item label
 * @returns {Function} return.isValidEmail - Validate email format
 * @returns {Function} return.isSafeImageUrl - Validate image URL safety
 * @returns {Function} return.areRequiredFieldsFilled - Check all required fields
 * @returns {Function} return.useEmailValidation - Create computed email validator
 * @returns {Function} return.useRequiredValidation - Create computed required validator
 * @returns {Function} return.useImageUrlValidation - Create computed URL validator
 * @returns {Function} return.useFormComplete - Create computed multi-field validator
 */
export function useFormValidation() {
  /**
   * Validates that a string is not empty after trimming
   * @param {string} value - Value to validate
   * @returns {boolean} True if non-empty
   */
  function isRequired(value) {
    return value != null && String(value).trim().length > 0;
  }

  /**
   * Validates string length is within bounds
   * @param {string} value - Value to validate
   * @param {number} min - Minimum length
   * @param {number} max - Maximum length
   * @returns {boolean} True if within bounds
   */
  function isLengthValid(value, min = 0, max = Infinity) {
    const len = String(value || "").trim().length;
    return len >= min && len <= max;
  }

  /**
   * Validates password meets minimum requirements
   * @param {string} password - Password to validate
   * @returns {boolean} True if meets requirements
   */
  function isPasswordValid(password) {
    return isLengthValid(password, MIN_PASSWORD_LENGTH);
  }

  /**
   * Validates item label length
   * @param {string} label - Label to validate
   * @returns {boolean} True if within max length
   */
  function isLabelValid(label) {
    return isRequired(label) && isLengthValid(label, 1, MAX_ITEM_LABEL_LENGTH);
  }

  /**
   * Creates a computed property for email validation
   * @param {Ref<string>} emailRef - Reactive email reference
   * @returns {ComputedRef<boolean>} Computed validation result
   */
  function useEmailValidation(emailRef) {
    return computed(() => isValidEmail(emailRef.value));
  }

  /**
   * Creates a computed property for required field validation
   * @param {Ref<string>} valueRef - Reactive value reference
   * @returns {ComputedRef<boolean>} Computed validation result
   */
  function useRequiredValidation(valueRef) {
    return computed(() => isRequired(valueRef.value));
  }

  /**
   * Creates a computed property for image URL validation
   * @param {Ref<string>} urlRef - Reactive URL reference
   * @returns {ComputedRef<boolean>} Computed validation result
   */
  function useImageUrlValidation(urlRef) {
    return computed(() => {
      const url = urlRef.value?.trim();
      return !url || isSafeImageUrl(url);
    });
  }

  /**
   * Creates a computed property that validates multiple fields are all valid
   * @param {...Ref<boolean>} validationRefs - Multiple validation refs to check
   * @returns {ComputedRef<boolean>} True if all validations pass
   */
  function useFormComplete(...validationRefs) {
    return computed(() => validationRefs.every((ref) => ref.value === true));
  }

  /**
   * Validates an entire object has all required fields filled
   * @param {Object} formData - Form data object
   * @param {string[]} requiredFields - Array of required field names
   * @returns {boolean} True if all required fields are filled
   */
  function areRequiredFieldsFilled(formData, requiredFields) {
    return requiredFields.every((field) => isRequired(formData[field]));
  }

  return {
    // Validators
    isRequired,
    isLengthValid,
    isPasswordValid,
    isLabelValid,
    isValidEmail,
    isSafeImageUrl,
    areRequiredFieldsFilled,

    // Computed helpers
    useEmailValidation,
    useRequiredValidation,
    useImageUrlValidation,
    useFormComplete,
  };
}
