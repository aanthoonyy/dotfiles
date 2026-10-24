return {
  {
    "folke/snacks.nvim",
    opts = { explorer = { enabled = false } },
    keys = {
      { "<leader>e", false },
      { "<leader>E", false },
      { "<leader>fe", false },
      { "<leader>fE", false },
    },
  },
  {
    "stevearc/oil.nvim",
    lazy = false,
    opts = {
      keymaps = {
        ["<Esc>"] = "actions.close",
      },
    },
    keys = {
      { "-", "<cmd>Oil<cr>", desc = "Open parent directory" },
      { "<leader>e", "<cmd>Oil<cr>", desc = "Explorer Oil" },
      { "<leader>fe", "<cmd>Oil<cr>", desc = "Explorer Oil" },
      {
        "<leader>E",
        function()
          require("oil").open(vim.fn.getcwd())
        end,
        desc = "Explorer Oil (cwd)",
      },
      {
        "<leader>fE",
        function()
          require("oil").open(vim.fn.getcwd())
        end,
        desc = "Explorer Oil (cwd)",
      },
    },
  },
}
