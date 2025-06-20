import axiosInstance from "utils/axios";

/**
 * Service for handling order and trade-related API operations.
 */
const OrderService = {
  /**
   * Get all trades for a specific account by account_name.
   * @param {string} accountName - The unique account_name
   * @returns {Promise<Array>} - Array of trades
   */
  getTradesByAccountName: async (accountName) => {
    try {
      const response = await axiosInstance.get(`api/v1/trades/get-trades/${accountName}`);
      return response.data || [];
    } catch (error) {
      console.error(`Error fetching trades for account "${accountName}":`, error);
      return [];
    }
  },

  /**
   * (Optional) Get order by order ID
   * @param {string} orderId
   * @returns {Promise<Object|null>}
   */
  getOrderById: async (orderId) => {
    try {
      const response = await axiosInstance.get(`api/v1/orders/get-order/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching order ${orderId}:`, error);
      return null;
    }
  },
};

export default OrderService;
