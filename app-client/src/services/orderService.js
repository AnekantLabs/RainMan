import axiosInstance from "utils/axios";
import OrdersAPI from "mock/api/orders";

// Flag to use mock API for development
const USE_MOCK_API = true;

/**
 * Service for handling order-related API operations
 * Adapts to the existing backend API structure
 */
const OrderService = {
  /**
   * Get orders for a specific account
   * @param {string} accountId - The ID of the account
   * @returns {Promise<Array>} - Promise resolving to an array of orders
   */
  getOrdersByAccount: async (accountId) => {
    if (USE_MOCK_API) {
      return OrdersAPI.getOrdersByAccount(accountId);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.get(
        `/orders/get-by-account/${accountId}`
      );

      // Transform the response data if needed to match expected frontend format
      // For example: date formatting, status mapping, etc.
      return response.data;
    } catch (error) {
      console.error(`Error fetching orders for account ${accountId}:`, error);
      // Return empty array on error
      return [];
    }
  },

  /**
   * Get order details by order ID
   * @param {string} orderId - The ID of the order
   * @returns {Promise<Object>} - Promise resolving to order details
   */
  getOrderById: async (orderId) => {
    if (USE_MOCK_API) {
      return OrdersAPI.getOrderById(orderId);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.get(`/orders/get-order/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching order ${orderId}:`, error);
      return null;
    }
  },

  /**
   * Get all open orders for an account
   * @param {string} accountId - The ID of the account
   * @returns {Promise<Array>} - Promise resolving to an array of open orders
   */
  getOpenOrdersByAccount: async (accountId) => {
    if (USE_MOCK_API) {
      return OrdersAPI.getOpenOrdersByAccount(accountId);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.get(
        `/orders/get-open-orders/${accountId}`
      );

      // Transform if needed for frontend consistency
      return response.data.map((order) => ({
        ...order,
        // Ensure the order has all required fields in the expected format
        status: order.status || "open",
        executed: order.executed || "0%",
      }));
    } catch (error) {
      console.error(
        `Error fetching open orders for account ${accountId}:`,
        error
      );
      return [];
    }
  },

  /**
   * Get order history for an account
   * @param {string} accountId - The ID of the account
   * @param {Object} params - Additional query parameters like page, limit, etc.
   * @returns {Promise<Array>} - Promise resolving to an array of historical orders
   */
  getOrderHistoryByAccount: async (accountId, params = {}) => {
    if (USE_MOCK_API) {
      return OrdersAPI.getOrderHistoryByAccount(accountId);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.get(
        `/orders/get-order-history/${accountId}`,
        { params }
      );

      // Transform if needed for frontend consistency
      return response.data.map((order) => ({
        ...order,
        // Ensure the order has all required fields in the expected format
        status: order.status || "closed",
        executed: order.executed || "100%",
      }));
    } catch (error) {
      console.error(
        `Error fetching order history for account ${accountId}:`,
        error
      );
      return [];
    }
  },
};

export default OrderService;
