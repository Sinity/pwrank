import { useToast } from "primevue/usetoast";
import { HttpError } from "../rest";
import {
  TOAST_DURATION_SHORT,
  TOAST_DURATION_NORMAL,
  TOAST_DURATION_LONG,
} from "../constants";

/**
 * Composable for standardized notification/toast messages.
 * Reduces boilerplate and ensures consistent UX across the application.
 *
 * @example
 * ```js
 * const { notifySuccess, notifyError } = useNotification();
 * notifySuccess("Item saved");
 * notifyError(error, "Failed to save item");
 * ```
 *
 * @returns {Object} Notification helper methods
 * @returns {Function} return.notifySuccess - Show success notification
 * @returns {Function} return.notifyError - Show error notification
 * @returns {Function} return.notifyWarn - Show warning notification
 * @returns {Function} return.notifyInfo - Show info notification
 * @returns {Function} return.withNotification - Wrap async operation with notifications
 */
export function useNotification() {
  const toast = useToast();

  /**
   * Extracts error message from various error types
   * @param {Error|HttpError|string} error - Error object or message string
   * @param {string} fallback - Fallback message if extraction fails
   * @returns {string} Extracted error message
   */
  function extractErrorMessage(error, fallback = "An unexpected error occurred.") {
    if (typeof error === "string") {
      return error;
    }
    if (error instanceof HttpError) {
      return error.payload?.message || fallback;
    }
    if (error instanceof Error) {
      return error.message || fallback;
    }
    return fallback;
  }

  /**
   * Show success notification
   * @param {string} summary - Title of the notification
   * @param {string} detail - Optional detailed message
   * @param {number} life - Duration in milliseconds (default: SHORT)
   */
  function notifySuccess(summary, detail = "", life = TOAST_DURATION_SHORT) {
    toast.add({
      severity: "success",
      summary,
      detail,
      life,
    });
  }

  /**
   * Show error notification
   * @param {Error|HttpError|string} error - Error object or message
   * @param {string} summary - Optional custom title (default: "Error")
   * @param {number} life - Duration in milliseconds (default: LONG)
   */
  function notifyError(
    error,
    summary = "Error",
    life = TOAST_DURATION_LONG
  ) {
    const detail = extractErrorMessage(error, "Unable to reach the backend.");
    toast.add({
      severity: "error",
      summary,
      detail,
      life,
    });
  }

  /**
   * Show warning notification
   * @param {string} summary - Title of the notification
   * @param {string} detail - Optional detailed message
   * @param {number} life - Duration in milliseconds (default: NORMAL)
   */
  function notifyWarn(summary, detail = "", life = TOAST_DURATION_NORMAL) {
    toast.add({
      severity: "warn",
      summary,
      detail,
      life,
    });
  }

  /**
   * Show info notification
   * @param {string} summary - Title of the notification
   * @param {string} detail - Optional detailed message
   * @param {number} life - Duration in milliseconds (default: NORMAL)
   */
  function notifyInfo(summary, detail = "", life = TOAST_DURATION_NORMAL) {
    toast.add({
      severity: "info",
      summary,
      detail,
      life,
    });
  }

  /**
   * Convenience wrapper for async operations with automatic error handling
   * @param {Function} asyncFn - Async function to execute
   * @param {Object} options - Configuration options
   * @param {string} options.successMessage - Message to show on success
   * @param {string} options.errorMessage - Custom error summary
   * @param {Function} options.onSuccess - Callback on success
   * @param {Function} options.onError - Callback on error
   * @returns {Promise<boolean>} True if successful, false if error occurred
   */
  async function withNotification(
    asyncFn,
    {
      successMessage = null,
      errorMessage = "Operation failed",
      onSuccess = null,
      onError = null,
    } = {}
  ) {
    try {
      const result = await asyncFn();
      if (successMessage) {
        notifySuccess(successMessage);
      }
      if (onSuccess) {
        onSuccess(result);
      }
      return true;
    } catch (error) {
      notifyError(error, errorMessage);
      if (onError) {
        onError(error);
      }
      return false;
    }
  }

  return {
    notifySuccess,
    notifyError,
    notifyWarn,
    notifyInfo,
    withNotification,
  };
}
