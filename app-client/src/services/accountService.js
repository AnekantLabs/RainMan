import axiosInstance from "utils/axios";

/**
 * Service for handling account-related API operations
 * Connects to FastAPI backend
 */
const AccountService = {
  /**
   * Get all accounts
   * @returns {Promise<Array>} - Promise resolving to an array of accounts
   */
  getAllAccounts: async () => {
    try {
      const response = await axiosInstance.get("api/v1/accounts/get-accounts");

      // Enhance data with placeholders for missing fields
      return response.data.map((account) => ({
        ...account,
        balance: "$0.00",      // Temporary placeholder
        performance: 50         // Temporary placeholder
      }));
    } catch (error) {
      console.error("Error fetching accounts:", error);
      return [];
    }
  },
    
  /**
   * Get all accounts along with totalWalletBalance from backend
   * @returns {Promise<Array>} - Array of account objects with wallet_info
   */
  getAccountInfo: async () => {
    try {
      const response = await axiosInstance.get("api/v1/accounts/get-account-info");
      return response.data.accounts || [];
    } catch (error) {
      console.error("Error fetching account info:", error);
      return [];
    }
  },

  /**
   * Get account details by ID
   * @param {string|number} accountId
   * @returns {Promise<Object|null>}
   */
  getAccountById: async (accountId) => {
    try {
      const response = await axiosInstance.get(`api/v1/accounts/get-account/${accountId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching account ${accountId}:`, error);
      return null;
    }
  },

  /**
   * Create a new account
   * @param {Object} accountData
   * @returns {Promise<Object>}
   */
  createAccount: async (accountData) => {
    try {
      const response = await axiosInstance.post("api/v1/accounts/create-account", accountData);
      return response.data;
    } catch (error) {
      console.error("Error creating account:", error);
      throw error;
    }
  },

  /**
   * Update an existing account
   * @param {string|number} accountId
   * @param {Object} accountData
   * @returns {Promise<Object>}
   */
  updateAccount: async (accountId, accountData) => {
    try {
      const response = await axiosInstance.put(`api/v1/accounts/update-account/${accountId}`, accountData);
      return response.data;
    } catch (error) {
      console.error(`Error updating account ${accountId}:`, error);
      throw error;
    }
  },

  /**
   * Delete an account
   * @param {string|number} accountId
   * @returns {Promise<boolean>}
   */
  deleteAccount: async (accountId) => {
    try {
      await axiosInstance.delete(`api/v1/accounts/delete-account/${accountId}`);
      return true;
    } catch (error) {
      console.error(`Error deleting account ${accountId}:`, error);
      return false;
    }
  },

  /**
   * Get account balance and performance metrics
   * @param {string|number} accountId
   * @returns {Promise<Object>}
   */
  getAccountMetrics: async (accountId) => {
    try {
      const response = await axiosInstance.get(`api/v1/accounts/get-metrics/${accountId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching metrics for account ${accountId}:`, error);
      return {
        balance: "N/A",
        performance: 0,
      };
    }
  },
};

export default AccountService;
