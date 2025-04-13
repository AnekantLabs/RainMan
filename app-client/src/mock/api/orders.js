/**
 * Mock order data for testing
 * This will be replaced by actual API endpoints when the backend is ready
 */

// Mock order data for different accounts
const mockOrdersData = {
  // Account 1 orders
  1: [
    {
      id: "1",
      date: "2025-02-26 10:32:08",
      market_pair: "ETH/USDT",
      side: "sell",
      type: "market",
      price: "2200.03",
      amount: "0.000527",
      executed: "100%",
      status: "closed",
      account_id: "1",
    },
    {
      id: "2",
      date: "2025-02-26 10:32:07",
      market_pair: "ETH/USDT",
      side: "buy",
      type: "market",
      price: "3485.72",
      amount: "0.000527",
      executed: "100%",
      status: "closed",
      account_id: "1",
    },
    {
      id: "3",
      date: "2025-02-26 10:31:53",
      market_pair: "ETH/USDT",
      side: "sell",
      type: "market",
      price: "2200.03",
      amount: "0.000527",
      executed: "100%",
      status: "closed",
      account_id: "1",
    },
    {
      id: "4",
      date: "2025-02-26 10:31:51",
      market_pair: "ETH/USDT",
      side: "buy",
      type: "market",
      price: "3485.72",
      amount: "0.000527",
      executed: "100%",
      status: "closed",
      account_id: "1",
    },
    {
      id: "5",
      date: "2025-02-26 00:30:57",
      market_pair: "MBC/USDT",
      side: "sell",
      type: "market",
      price: "0.0000195",
      amount: "1.7K",
      executed: "100%",
      status: "closed",
      account_id: "1",
    },
    {
      id: "11",
      date: "2025-02-27 14:25:18",
      market_pair: "ETH/USDT",
      side: "buy",
      type: "limit",
      price: "3250.50",
      amount: "0.01",
      executed: "0%",
      status: "open",
      account_id: "1",
    },
  ],

  // Account 2 orders
  2: [
    {
      id: "6",
      date: "2025-02-26 00:30:01",
      market_pair: "NEXA/USDT",
      side: "sell",
      type: "market",
      price: "0.0000121",
      amount: "1.62K",
      executed: "100%",
      status: "closed",
      account_id: "2",
    },
    {
      id: "7",
      date: "2025-02-20 19:30:49",
      market_pair: "MBC/USDT",
      side: "sell",
      type: "market",
      price: "0.0000251",
      amount: "55.98K",
      executed: "100%",
      status: "closed",
      account_id: "2",
    },
    {
      id: "12",
      date: "2025-02-27 10:12:32",
      market_pair: "BTC/USDT",
      side: "buy",
      type: "limit",
      price: "95,000",
      amount: "0.002",
      executed: "0%",
      status: "open",
      account_id: "2",
    },
  ],

  // Account 3 orders
  3: [
    {
      id: "8",
      date: "2025-02-20 19:30:37",
      market_pair: "NEXA/USDT",
      side: "sell",
      type: "market",
      price: "0.000012",
      amount: "53.3K",
      executed: "100%",
      status: "closed",
      account_id: "3",
    },
  ],

  // Account 4 orders
  4: [
    {
      id: "9",
      date: "2025-02-19 14:36:33",
      market_pair: "BTC/USDT",
      side: "sell",
      type: "market",
      price: "90,200",
      amount: "0.00000149",
      executed: "100%",
      status: "closed",
      account_id: "4",
    },
    {
      id: "10",
      date: "2025-02-19 14:31:48",
      market_pair: "BTC/USDT",
      side: "buy",
      type: "market",
      price: "97,000",
      amount: "0.00000149",
      executed: "100%",
      status: "closed",
      account_id: "4",
    },
    {
      id: "13",
      date: "2025-02-28 09:15:22",
      market_pair: "ETH/USDT",
      side: "sell",
      type: "limit",
      price: "3600.00",
      amount: "0.5",
      executed: "0%",
      status: "open",
      account_id: "4",
    },
    {
      id: "14",
      date: "2025-02-28 09:22:14",
      market_pair: "BTC/USDT",
      side: "buy",
      type: "limit",
      price: "92,500",
      amount: "0.01",
      executed: "0%",
      status: "open",
      account_id: "4",
    },
  ],

  // Account 5 orders
  5: [
    {
      id: "15",
      date: "2025-02-25 15:42:11",
      market_pair: "BTC/USDT",
      side: "buy",
      type: "market",
      price: "94,500",
      amount: "0.0025",
      executed: "100%",
      status: "closed",
      account_id: "5",
    },
    {
      id: "16",
      date: "2025-02-26 08:31:05",
      market_pair: "ETH/USDT",
      side: "sell",
      type: "market",
      price: "3300.25",
      amount: "0.15",
      executed: "100%",
      status: "closed",
      account_id: "5",
    },
  ],
};

// Ensure all mock orders use proper percentage values for executed field
const ensureProperExecuted = (orders) => {
  return orders.map((order) => {
    // Make sure executed values are proper percentages
    let executed = order.executed;

    // If executed doesn't end with %, add it
    if (!executed.endsWith("%")) {
      executed = executed + "%";
    }

    // If executed is a number without %, convert it
    if (!isNaN(executed.replace("%", ""))) {
      // Remove self-assignment: executed = executed;
    }

    return {
      ...order,
      executed,
    };
  });
};

/**
 * Mock API functions for orders
 */
const OrdersAPI = {
  /**
   * Get all orders for a specific account
   * @param {string} accountId - The account ID
   * @returns {Promise<Array>} - Promise resolving to an array of orders
   */
  getOrdersByAccount: (accountId) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        const orders = mockOrdersData[accountId] || [];
        resolve(ensureProperExecuted(orders));
      }, 500);
    });
  },

  /**
   * Get only open orders for a specific account
   * @param {string} accountId - The account ID
   * @returns {Promise<Array>} - Promise resolving to an array of open orders
   */
  getOpenOrdersByAccount: (accountId) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        const allOrders = mockOrdersData[accountId] || [];
        const openOrders = allOrders.filter((order) => order.status === "open");
        resolve(ensureProperExecuted(openOrders));
      }, 500);
    });
  },

  /**
   * Get order history (closed orders) for a specific account
   * @param {string} accountId - The account ID
   * @returns {Promise<Array>} - Promise resolving to an array of closed orders
   */
  getOrderHistoryByAccount: (accountId) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        const allOrders = mockOrdersData[accountId] || [];
        const closedOrders = allOrders.filter(
          (order) => order.status === "closed"
        );
        resolve(ensureProperExecuted(closedOrders));
      }, 500);
    });
  },

  /**
   * Get a specific order by ID
   * @param {string} orderId - The order ID
   * @returns {Promise<Object|null>} - Promise resolving to order details or null if not found
   */
  getOrderById: (orderId) => {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        // Search through all accounts for the specified order
        for (const accountId in mockOrdersData) {
          const orders = mockOrdersData[accountId];
          const order = orders.find((o) => o.id === orderId);
          if (order) {
            resolve(order);
            return;
          }
        }
        resolve(null);
      }, 500);
    });
  },
};

export default OrdersAPI;
