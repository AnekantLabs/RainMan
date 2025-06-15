import axiosInstance from "utils/axios";

/**
 * Service for handling alert-related API operations.
 */
const AlertService = {
  /**
   * Get the latest alerts (e.g., last 2).
   * @returns {Promise<Array>} - List of alert JSONs
   */
  getLatestAlerts: async () => {
    try {
      const response = await axiosInstance.get("/alerts/latest");
      return response.data || [];
    } catch (error) {
      console.error("Error fetching latest alerts:", error);
      return [];
    }
  },

  /**
   * Send/resend a TradingView-style alert to the backend.
   * @param {Object} alertData - JSON alert object to send
   * @returns {Promise<Object>} - Backend response
   */
  sendAlert: async (alertData) => {
    try {
      const response = await axiosInstance.post("/alerts/receive-tradingview-alert", alertData);
      return response.data;
    } catch (error) {
      console.error("Error sending alert:", error);
      throw error;
    }
  },
};

export default AlertService;
