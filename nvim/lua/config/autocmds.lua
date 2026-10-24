-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
--
-- Add any additional autocmds here
-- with `vim.api.nvim_create_autocmd`
--
-- Or remove existing autocmds by their group name (which is prefixed with `lazyvim_` for the defaults)
-- e.g. vim.api.nvim_del_augroup_by_name("lazyvim_wrap_spell")

if vim.env.KITTY_WINDOW_ID then
  local function terminal_background(reset)
    local color = vim.api.nvim_get_hl(0, { name = "Normal", link = false }).bg
    local sequence = reset and "\027]111\007" or (color and string.format("\027]11;#%06x\007", color))
    if sequence then
      io.stdout:write(sequence)
      io.stdout:flush()
    end
  end

  local group = vim.api.nvim_create_augroup("kitty_background", { clear = true })
  vim.api.nvim_create_autocmd({ "UIEnter", "ColorScheme", "VimResume" }, {
    group = group,
    callback = function()
      terminal_background(false)
    end,
  })
  vim.api.nvim_create_autocmd({ "VimLeavePre", "VimSuspend" }, {
    group = group,
    callback = function()
      terminal_background(true)
    end,
  })
  terminal_background(false)
end
