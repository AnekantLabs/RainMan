import axiosInstance from "utils/axios";
import AccountsAPI from "mock/api/accounts";

// Flag to use mock API for development
const USE_MOCK_API = true;

/**
 * Service for handling account-related API operations
 * Adapts to the existing backend API structure
 */
const AccountService = {
  /**
   * Get all accounts
   * @returns {Promise<Array>} - Promise resolving to an array of accounts
   */
  getAllAccounts: async () => {
    if (USE_MOCK_API) {
      return AccountsAPI.getAllAccounts();
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.get("/accounts/get-accounts");
      // Process response if needed to match expected format
      return response.data;
    } catch (error) {
      console.error("Error fetching accounts:", error);
      // Return empty array on error
      return [];
    }
  },

  /**
   * Get account details by ID
   * @param {string} accountId - The ID of the account
   * @returns {Promise<Object>} - Promise resolving to account details
   */
  getAccountById: async (accountId) => {
    if (USE_MOCK_API) {
      return AccountsAPI.getAccountById(accountId);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.get(
        `/accounts/get-account/${accountId}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching account ${accountId}:`, error);
      return null;
    }
  },

  /**
   * Create a new account
   * @param {Object} accountData - The account data to create
   * @returns {Promise<Object>} - Promise resolving to the created account
   */
  createAccount: async (accountData) => {
    if (USE_MOCK_API) {
      return AccountsAPI.createAccount(accountData);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.post(
        "/accounts/create-account",
        accountData
      );
      return response.data;
    } catch (error) {
      console.error("Error creating account:", error);
      throw error; // Re-throw to allow handling by the component
    }
  },

  /**
   * Update an existing account
   * @param {string} accountId - The ID of the account to update
   * @param {Object} accountData - The updated account data
   * @returns {Promise<Object>} - Promise resolving to the updated account
   */
  updateAccount: async (accountId, accountData) => {
    if (USE_MOCK_API) {
      return AccountsAPI.updateAccount(accountId, accountData);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.put(
        `/accounts/update-account/${accountId}`,
        accountData
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating account ${accountId}:`, error);
      throw error; // Re-throw to allow handling by the component
    }
  },

  /**
   * Delete an account
   * @param {string} accountId - The ID of the account to delete
   * @returns {Promise<boolean>} - Promise resolving to success status
   */
  deleteAccount: async (accountId) => {
    if (USE_MOCK_API) {
      return AccountsAPI.deleteAccount(accountId);
    }

    try {
      // Adapt to backend API structure
      await axiosInstance.delete(`/accounts/delete-account/${accountId}`);
      return true;
    } catch (error) {
      console.error(`Error deleting account ${accountId}:`, error);
      return false;
    }
  },

  /**
   * Get account balance and performance metrics
   * @param {string} accountId - The ID of the account
   * @returns {Promise<Object>} - Promise resolving to account metrics
   */
  getAccountMetrics: async (accountId) => {
    if (USE_MOCK_API) {
      return AccountsAPI.getAccountMetrics(accountId);
    }

    try {
      // Adapt to backend API structure
      const response = await axiosInstance.get(
        `/accounts/get-metrics/${accountId}`
      );
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
