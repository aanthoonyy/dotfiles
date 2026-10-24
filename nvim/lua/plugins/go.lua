return {
  {
    "mason-org/mason.nvim",
    opts = function(_, opts)
      opts.ensure_installed = vim.tbl_filter(function(tool)
        return tool ~= "golangci-lint"
      end, opts.ensure_installed or {})
    end,
  },
  {
    "mfussenegger/nvim-lint",
    opts = {
      linters_by_ft = {
        go = {},
      },
    },
  },
}
