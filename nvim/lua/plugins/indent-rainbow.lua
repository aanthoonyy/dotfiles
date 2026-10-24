return {
  {
    "folke/snacks.nvim",
    opts = function(_, opts)
      local colors = {
        "#dc322f", -- red
        "#cb4b16", -- orange
        "#b58900", -- yellow
        "#859900", -- green
        "#2aa198", -- cyan
        "#268bd2", -- blue
        "#6c71c4", -- violet
      }
      local groups = {}
      for i in ipairs(colors) do
        groups[i] = "RainbowIndent" .. i
      end
      local function highlights()
        for i, color in ipairs(colors) do
          vim.api.nvim_set_hl(0, groups[i], { fg = color, nocombine = true })
        end
      end
      vim.api.nvim_create_autocmd("ColorScheme", {
        group = vim.api.nvim_create_augroup("rainbow_indent_colors", { clear = true }),
        callback = highlights,
      })
      highlights()

      opts.indent = vim.tbl_deep_extend("force", opts.indent or {}, {
        enabled = true,
        indent = { enabled = true, hl = groups },
        scope = { enabled = false },
      })
    end,
  },
}
