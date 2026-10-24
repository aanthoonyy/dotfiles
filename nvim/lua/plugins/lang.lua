return {
  -- Extra treesitter parsers not covered by the typescript/clangd extras
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      vim.list_extend(opts.ensure_installed, {
        "css",
        "html",
        "cmake",
        "c",
        "cpp",
      })
    end,
  },

  -- CSS and HTML language servers for React projects
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        cssls = {},
        html = {},
        cmake = {},
      },
    },
  },

  -- Additional mason tools: debuggers + cmake tooling
  {
    "mason-org/mason.nvim",
    opts = {
      ensure_installed = {
        -- C/C++ debugger
        "codelldb",
        -- CMake support
        "cmake-language-server",
        "cmakelang",
        -- JS/TS debugger
        "js-debug-adapter",
      },
    },
  },

  -- C/C++ debug adapter (codelldb)
  {
    "mfussenegger/nvim-dap",
    optional = true,
    config = function()
      local dap = require("dap")
      dap.adapters.codelldb = {
        type = "server",
        port = "${port}",
        executable = {
          command = vim.fn.exepath("codelldb"),
          args = { "--port", "${port}" },
        },
      }
      for _, lang in ipairs({ "c", "cpp" }) do
        dap.configurations[lang] = {
          {
            name = "Launch (codelldb)",
            type = "codelldb",
            request = "launch",
            program = function()
              return vim.fn.input("Path to executable: ", vim.fn.getcwd() .. "/", "file")
            end,
            cwd = "${workspaceFolder}",
            stopOnEntry = false,
          },
        }
      end

      -- JS/TS via vscode-js-debug; path resolved lazily so it works before first install
      dap.adapters["pwa-node"] = {
        type = "server",
        host = "localhost",
        port = "${port}",
        executable = {
          command = "node",
          args = {
            vim.fn.stdpath("data")
              .. "/mason/packages/js-debug-adapter/js-debug/src/dapDebugServer.js",
            "${port}",
          },
        },
      }
      for _, lang in ipairs({ "javascript", "typescript", "javascriptreact", "typescriptreact" }) do
        dap.configurations[lang] = {
          {
            name = "Launch (Node)",
            type = "pwa-node",
            request = "launch",
            program = "${file}",
            cwd = "${workspaceFolder}",
            sourceMaps = true,
          },
        }
      end
    end,
  },
}
